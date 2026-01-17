import {
  Component,
  EventEmitter,
  HostListener,
  inject,
  Input,
  OnInit,
  Output,
} from '@angular/core';
import {
  animate,
  AnimationEvent,
  style,
  transition,
  trigger,
} from '@angular/animations';
import { ImageGallery } from '../../../../modules/core/api/v1';

@Component({
  selector: 'app-lightbox',
  templateUrl: './lightbox.component.html',
  styleUrls: ['./lightbox.component.scss'],
  standalone: true, // If using standalone components
  animations: [
    trigger('animation-enter', [
      transition('void => visible', [
        style({ transform: 'scale(0.5)' }),
        animate('150ms', style({ transform: 'scale(1)' })),
      ]),
      transition('visible => void', [
        style({ transform: 'scale(1)' }),
        animate('150ms', style({ transform: 'scale(0.5)' })),
      ]),
    ]),
    trigger('animation-leave', [
      transition(':leave', [
        style({ opacity: 1 }),
        animate('250ms', style({ opacity: 0.8 })),
      ]),
    ]),
  ],
})
export class LightboxComponent implements OnInit {
  @Input() currentLightboxImg: ImageGallery | undefined;
  @Input() imageNum: number = 0;
  @Input() totalImageCount: number = 0;
  @Input() controls: boolean = true;
  @Input() previewImage: boolean = false;

  @Output() close = new EventEmitter<void>();
  @Output() prevAction = new EventEmitter<void>();
  @Output() nextAction = new EventEmitter<void>();
  @Output() animationEnd = new EventEmitter<AnimationEvent>();

  innerWidth = 0;
  innerHeight = 0;

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

  onclosePreview(): void {
    this.close.emit();
  }

  prev(): void {
    this.prevAction.emit();
  }

  next(): void {
    this.nextAction.emit();
  }

  onAnimationEnd(event: AnimationEvent): void {
    this.animationEnd.emit(event);
  }

  getIndex(): number {
    return this.imageNum;
  }

  getLightboxRenderWidth(): number {
    if (typeof window !== 'undefined') {
      const width = Math.min(
        this.innerWidth * (window.devicePixelRatio || 1),
        2500
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
      (imageWidth / imageHeight) * Math.floor(this.innerHeight * 0.8)
    );
  }

  getGalleryImageHeight(imageWidth: number, imageHeight: number): number {
    if (imageHeight < imageWidth) {
      return Math.floor(
        (imageHeight / imageWidth) * Math.floor(this.innerWidth * 0.7)
      );
    }
    return Math.floor(this.innerHeight * 0.8);
  }
}
