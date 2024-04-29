import { Component, Input, OnInit } from '@angular/core';
import { Item } from '../../models/item';
import {
  animate,
  style,
  transition,
  trigger,
  AnimationEvent,
} from '@angular/animations';

@Component({
  selector: 'app-gallery-lightbox',
  standalone: false,
  templateUrl: './gallery-lightbox.component.html',
  styleUrl: './gallery-lightbox.component.scss',
  animations: [
    trigger('animation', [
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
export class GalleryLightboxComponent implements OnInit {
  @Input() galleryData: Item[] = [];
  @Input() showCount = false;

  previewImage = false;
  showMask = false;
  currentLightboxImg: Item = this.galleryData[0];
  currentIndex = 0;
  controls = true;
  totalImageCount = 0;

  constructor() {}
  ngOnInit(): void {
    this.totalImageCount = this.galleryData.length;
  }

  onPreviewImage(index: number): void {
    console.log('Preview image', index);

    this.showMask = true;
    this.previewImage = true;

    this.currentIndex = index;
    this.currentLightboxImg = this.galleryData[index];
  }

  onAnimationEnd(event: AnimationEvent): void {
    if (event.toState === 'void') {
      this.showMask = false;
      this.previewImage = false;
    }
  }

  onclosePreview(): void {
    this.previewImage = false;
  }

  prev(): void {
    this.currentIndex--;
    if (this.currentIndex < 0) {
      this.currentIndex = this.galleryData.length - 1;
    }
    this.currentLightboxImg = this.galleryData[this.currentIndex];
  }

  next(): void {
    this.currentIndex++;
    if (this.currentIndex > this.galleryData.length - 1) {
      this.currentIndex = 0;
    }
    this.currentLightboxImg = this.galleryData[this.currentIndex];
  }
}
