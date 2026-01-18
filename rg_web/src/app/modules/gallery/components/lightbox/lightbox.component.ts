import {
  Component,
  EventEmitter,
  HostListener,
  OnInit,
  Output,
  effect,
  input,
  signal,
} from '@angular/core';
import { NgClass } from '@angular/common';
import { ImageGallery } from '../../../../modules/core/api/v1';

@Component({
  selector: 'app-lightbox',
  templateUrl: './lightbox.component.html',
  styleUrls: ['./lightbox.component.scss'],
  standalone: true, // If using standalone components
  imports: [NgClass],
})
export class LightboxComponent implements OnInit {
  readonly currentLightboxImg = input<ImageGallery>();
  readonly previousLightboxImg = signal<ImageGallery | undefined>(undefined);
  readonly lastLightboxImg = signal<ImageGallery | undefined>(undefined);
  readonly imageNum = input<number>(0);
  readonly totalImageCount = input<number>(0);
  readonly controls = input<boolean>(true);
  readonly previewImage = input<boolean>(false);
  readonly pageFlipDirection = input<'next' | 'prev'>('next');
  readonly isLoading = signal(true);

  @Output() close = new EventEmitter<void>();
  @Output() prevAction = new EventEmitter<void>();
  @Output() nextAction = new EventEmitter<void>();
  @Output() animationEnd = new EventEmitter<TransitionEvent>();

  readonly imageAnimA = signal(true);

  innerWidth = 0;
  innerHeight = 0;

  constructor() {
    effect(() => {
      this.imageNum();
      this.imageAnimA.update((value) => !value);
    });

    effect(
      () => {
        const nextImg = this.currentLightboxImg();
        const lastImg = this.lastLightboxImg();

        if (nextImg && nextImg !== lastImg) {
          this.previousLightboxImg.set(lastImg);
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
    }
  }

  @HostListener('window:resize', ['$event'])
  onResize(event: any) {
    if (typeof window !== 'undefined') {
      this.innerWidth = window.innerWidth;
      this.innerHeight = window.innerHeight;
    }
  }

  @HostListener('document:keydown.escape', ['$event'])
  onKeydownEscapeHandler(event: Event) {
    this.close.emit();
  }

  @HostListener('document:keydown.arrowLeft', ['$event'])
  onKeydownLeftHandler(event: Event) {
    this.prevAction.emit();
  }

  @HostListener('document:keydown.arrowRight', ['$event'])
  onKeydownRightHandler(event: Event) {
    this.nextAction.emit();
  }

  onImageLoad(): void {
    this.isLoading.set(false);
  }

  onclosePreview(): void {
    this.close.emit();
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
      const width = Math.min(
        this.innerWidth * (window.devicePixelRatio || 1),
        2500,
      );
      return Math.floor(width);
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
