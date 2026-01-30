import {
  Component,
  EventEmitter,
  HostListener,
  OnInit,
  OnDestroy,
  Output,
  effect,
  input,
  signal,
  inject,
  ChangeDetectionStrategy,
} from '@angular/core';
import {
  NgClass,
  DOCUMENT,
  DatePipe,
  isPlatformBrowser,
} from '@angular/common';
import { ImageGallery } from '../../../../modules/core/api/v1';
import { PLATFORM_ID, viewChild, ElementRef } from '@angular/core';
import type { Map as LeafletMap } from 'leaflet';

@Component({
  selector: 'app-lightbox',
  templateUrl: './lightbox.component.html',
  styleUrls: ['./lightbox.component.scss'],
  standalone: true,
  imports: [NgClass, DatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LightboxComponent implements OnInit, OnDestroy {
  private document = inject<Document>(DOCUMENT);
  private platformId = inject(PLATFORM_ID);

  private map: LeafletMap | undefined; // Leaflet map instance

  readonly currentLightboxImg = input<ImageGallery>();
  readonly previousLightboxImg = signal<ImageGallery | undefined>(undefined);
  readonly lastLightboxImg = signal<ImageGallery | undefined>(undefined);
  readonly imageNum = input<number>(0);
  readonly totalImageCount = input<number>(0);
  readonly controls = input<boolean>(true);
  readonly previewImage = input<boolean>(false);
  readonly pageFlipDirection = input<'next' | 'prev'>('next');
  readonly isLoading = signal(true);
  readonly showInfo = signal(false);

  // ViewChild for the map container
  readonly mapContainer = viewChild<ElementRef>('mapContainer');

  @Output() closeLightbox = new EventEmitter<void>();
  @Output() prevAction = new EventEmitter<void>();
  @Output() nextAction = new EventEmitter<void>();
  @Output() animationEnd = new EventEmitter<TransitionEvent>();

  readonly imageAnimA = signal(true);

  innerWidth = 0;
  innerHeight = 0;

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
      this.imageNum();
      this.imageAnimA.update((value) => !value);
      this.showInfo.set(false);
    });

    effect(() => {
      const container = this.mapContainer()?.nativeElement;
      const img = this.currentLightboxImg();
      const infoVisible = this.showInfo();

      if (
        infoVisible &&
        container &&
        img?.latitude &&
        img?.longitude &&
        isPlatformBrowser(this.platformId)
      ) {
        // Dynamic import to avoid SSR issues
        import('leaflet').then((module) => {
          const L = module.default as any;
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
            map.invalidateSize();
          }, 100);
        });
      }
    });

    effect(
      () => {
        const nextImg = this.currentLightboxImg();
        const lastImg = this.lastLightboxImg();

        if (nextImg && nextImg !== lastImg) {
          this.previousLightboxImg.set(undefined);
          this.lastLightboxImg.set(nextImg);
          this.isLoading.set(true);
        }
      },
      { allowSignalWrites: true },
    );
  }

  ngOnInit(): void {
    if (typeof window !== 'undefined') {
      this.innerWidth = window.innerWidth;
      this.innerHeight = window.innerHeight;
      this.document.body.style.overflow = 'hidden';
    }
  }

  ngOnDestroy(): void {
    if (typeof window !== 'undefined') {
      this.document.body.style.overflow = '';
    }
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

  onLightboxTransitionEnd(event: TransitionEvent): void {
    if (!this.previewImage() && event.propertyName === 'opacity') {
      this.animationEnd.emit(event);
    }
  }

  getIndex(): number {
    return this.imageNum();
  }

  getLightboxRenderWidth(): number {
    if (typeof window !== 'undefined') {
      const target = this.innerWidth * (window.devicePixelRatio || 1);
      const buckets = [400, 600, 800, 1000, 1200, 1600, 2000, 2500];
      const match = buckets.find((b) => b >= target);
      return match || 2500;
    }
    return 1200;
  }

  getGalleryImageWidth(imageWidth: number, imageHeight: number): number {
    if (imageHeight < imageWidth) {
      return Math.floor(this.innerWidth * 0.7);
    }
    return Math.floor(
      (imageWidth / imageHeight) * Math.floor(this.innerHeight * 0.8),
    );
  }

  getGalleryImageHeight(imageWidth: number, imageHeight: number): number {
    if (imageHeight < imageWidth) {
      return Math.floor(
        (imageHeight / imageWidth) * Math.floor(this.innerWidth * 0.7),
      );
    }
    return Math.floor(this.innerHeight * 0.8);
  }
}
