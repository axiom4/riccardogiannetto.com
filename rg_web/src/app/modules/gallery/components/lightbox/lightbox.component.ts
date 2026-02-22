import {
  Component,
  EventEmitter,
  HostListener,
  Output,
  effect,
  input,
  signal,
  inject,
  computed,
  ChangeDetectionStrategy,
  DestroyRef,
  ViewEncapsulation,
} from '@angular/core';
import { Title, Meta } from '@angular/platform-browser';
import {
  NgClass,
  NgOptimizedImage,
  DOCUMENT,
  DatePipe,
  isPlatformBrowser,
  IMAGE_LOADER,
  ImageLoaderConfig,
} from '@angular/common';
import { ImageGallery } from '../../../../modules/core/api/v1';
import { PLATFORM_ID, viewChild, ElementRef } from '@angular/core';
import type { Map as LeafletMap } from 'leaflet';
import { environment } from '../../../../../environments/environment';

export const lightboxImageLoader = (config: ImageLoaderConfig) => {
  const src = config.src;
  // If src is a full URL, return it (bypassing resize)
  if (src.startsWith('http') || src.startsWith('/')) {
    return src;
  }

  let baseUrl = environment.api_url;
  if (baseUrl.endsWith('/')) {
    baseUrl = baseUrl.slice(0, -1);
  }

  // Construct resized URL: /portfolio/images/<ID>/width/<WIDTH>
  // Note: The backend expects integer width. NgOptimizedImage provides it.
  const width = config.width || 1200;
  return `${baseUrl}/portfolio/images/${src}/width/${width}`;
};

@Component({
  selector: 'app-lightbox',
  templateUrl: './lightbox.component.html',
  styleUrl: './lightbox.component.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None,
  imports: [NgClass, NgOptimizedImage, DatePipe],
  providers: [
    {
      provide: IMAGE_LOADER,
      useValue: lightboxImageLoader,
    },
  ],
})
export class LightboxComponent {
  private document = inject<Document>(DOCUMENT);
  private platformId = inject(PLATFORM_ID);
  private titleService = inject(Title);
  private metaService = inject(Meta);

  private map: LeafletMap | undefined; // Leaflet map instance

  readonly currentLightboxImg = input<ImageGallery>();
  readonly previousLightboxImg = signal<ImageGallery | undefined>(undefined);
  readonly lastLightboxImg = signal<ImageGallery | undefined>(undefined);
  readonly imageNum = input<number>(0);
  readonly totalImageCount = input<number>(0);
  readonly controls = input<boolean>(true);
  readonly previewImage = input<boolean>(false);
  readonly pageFlipDirection = input<'next' | 'prev'>('next');
  readonly preloadImages = input<ImageGallery[]>([]); // New input for preloading
  readonly isLoading = signal(true);
  readonly showInfo = signal(false);

  readonly hasInfo = computed(() => {
    const img = this.currentLightboxImg();
    if (!img) return false;
    return !!(
      img.camera_model ||
      img.lens_model ||
      img.iso_speed ||
      img.aperture_f_number ||
      img.shutter_speed ||
      img.focal_length ||
      img.date ||
      (img.latitude && img.longitude)
    );
  });

  // ViewChild for the map container
  readonly mapContainer = viewChild<ElementRef>('mapContainer');

  @Output() closeLightbox = new EventEmitter<void>();
  @Output() prevAction = new EventEmitter<void>();
  @Output() nextAction = new EventEmitter<void>();
  @Output() animationEnd = new EventEmitter<TransitionEvent>();

  readonly imageAnimA = signal(true);

  innerWidth = 0;
  innerHeight = 0;

  getImgId(img: ImageGallery): string {
    if (!img || !img.url) return '';

    // Pattern to find the ID after 'images/'
    const match = img.url.match(/images\/([^/]+)/);

    if (match && match[1]) {
      return match[1]; // Return just the ID
    }

    return img.url; // Fallback to full URL if extraction fails
  }

  toggleInfo() {
    this.showInfo.update((v) => !v);
  }

  formatShutterSpeed(val: number | null | undefined): string {
    if (val === null || val === undefined || val === 0) return '';

    if (val >= 1) {
      return Math.round(val) + '"';
    }
    const denominator = Math.round(1 / val);
    return '1/' + denominator;
  }

  constructor() {
    effect(() => {
      const currentImg = this.currentLightboxImg();
      const showPreview = this.previewImage();
      if (currentImg && showPreview) {
        this.updateTitleMeta(currentImg);
      } else {
        this.clearTitleMeta();
      }
    });

    effect(() => {
      this.imageNum();
      this.imageAnimA.update((value) => !value);
      this.showInfo.set(false);
    });

    effect((onCleanup) => {
      const container = this.mapContainer()?.nativeElement;
      const img = this.currentLightboxImg();
      const infoVisible = this.showInfo();

      let isCleanedUp = false;
      onCleanup(() => {
        isCleanedUp = true;
        if (this.map) {
          this.map.remove();
          this.map = undefined;
        }
      });

      if (
        infoVisible &&
        container &&
        img?.latitude &&
        img?.longitude &&
        isPlatformBrowser(this.platformId)
      ) {
        // Dynamic import to avoid SSR issues
        import('leaflet').then((module) => {
          if (isCleanedUp) return;

          const L = module.default as typeof import('leaflet');
          const defaultIcon = L.icon({
            iconUrl: '/assets/leaflet/marker-icon.png',
            iconRetinaUrl: '/assets/leaflet/marker-icon-2x.png',
            shadowUrl: '/assets/leaflet/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            tooltipAnchor: [16, -28],
            shadowSize: [41, 41],
          });

          // Cleanup existing map if specific logic needed, though we usually recreate
          if (this.map) {
            this.map.remove();
          }

          if (!container.clientWidth) return; // wait for render

          const map = L.map(container).setView(
            [img.latitude!, img.longitude!],
            13,
          );
          this.map = map;

          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution:
              '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
          }).addTo(map);

          L.marker([img.latitude!, img.longitude!], {
            icon: defaultIcon,
          }).addTo(map);

          // Fix gray map issue by invalidating size after a tick
          setTimeout(() => {
            if (!isCleanedUp && this.map) {
              map.invalidateSize();
            }
          }, 100);
        });
      }
    });

    effect(() => {
      const nextImg = this.currentLightboxImg();
      const lastImg = this.lastLightboxImg();

      if (nextImg && nextImg !== lastImg) {
        this.previousLightboxImg.set(lastImg);
        this.lastLightboxImg.set(nextImg);
        this.isLoading.set(true);
      }
    });

    if (isPlatformBrowser(this.platformId)) {
      this.innerWidth = window.innerWidth;
      this.innerHeight = window.innerHeight;
      this.document.body.style.overflow = 'hidden';
    }

    inject(DestroyRef).onDestroy(() => {
      if (isPlatformBrowser(this.platformId)) {
        this.document.body.style.overflow = '';
      }
    });
  }

  @HostListener('window:resize')
  onResize() {
    if (typeof window !== 'undefined') {
      this.innerWidth = window.innerWidth;
      this.innerHeight = window.innerHeight;
    }
  }

  @HostListener('document:keydown.escape')
  onKeydownEscapeHandler() {
    this.closeLightbox.emit();
  }

  @HostListener('document:keydown.arrowLeft')
  onKeydownLeftHandler() {
    this.prevAction.emit();
  }

  @HostListener('document:keydown.arrowRight')
  onKeydownRightHandler() {
    this.nextAction.emit();
  }

  onImageLoad(): void {
    this.isLoading.set(false);
    this.imageAnimA.update((v) => !v);
  }

  onclosePreview(): void {
    this.closeLightbox.emit();
  }

  prev(): void {
    this.prevAction.emit();
  }

  next(): void {
    this.nextAction.emit();
  }

  onLightboxTransitionEnd(event: Event): void {
    const transitionEvent = event as TransitionEvent;
    if (!this.previewImage() && transitionEvent.propertyName === 'opacity') {
      this.animationEnd.emit(transitionEvent);
    }
  }

  getIndex(): number {
    return this.imageNum();
  }

  private updateTitleMeta(image: ImageGallery): void {
    const title = `${image.title} - Riccardo Giannetto`;
    const description = `${image.title} by ${image.author}. Fine art nature photography.`;
    const url = window.location.href; // The URL is updated by GalleryLightboxComponent
    const imageUrl = image.image; // Assuming image field is the URL

    this.titleService.setTitle(title);
    this.updateCanonical(url);

    this.metaService.updateTag({ name: 'description', content: description });
    this.metaService.updateTag({ property: 'og:title', content: title });
    this.metaService.updateTag({
      property: 'og:description',
      content: description,
    });
    this.metaService.updateTag({ property: 'og:image', content: imageUrl });
    this.metaService.updateTag({ property: 'og:url', content: url });
    this.metaService.updateTag({
      name: 'twitter:card',
      content: 'summary_large_image',
    });
  }

  private clearTitleMeta(): void {
    const url = window.location.href; // Get current URL (should be base)
    this.updateCanonical(url);
    this.titleService.setTitle('Riccardo Giannetto - Wild Nature Photography');
    this.metaService.updateTag({
      name: 'description',
      content: 'Fine Art Nature Photography by Riccardo Giannetto',
    });
    this.metaService.removeTag("property='og:title'");
    this.metaService.removeTag("property='og:description'");
    this.metaService.removeTag("property='og:image'");
    this.metaService.removeTag("property='og:url'");
    this.metaService.removeTag("name='twitter:card'");
  }

  private updateCanonical(url: string) {
    let link: HTMLLinkElement | null = this.document.querySelector(
      "link[rel='canonical']",
    );
    if (!link) {
      link = this.document.createElement('link');
      link.setAttribute('rel', 'canonical');
      this.document.head.appendChild(link);
    }
    link.setAttribute('href', url);
  }
}
