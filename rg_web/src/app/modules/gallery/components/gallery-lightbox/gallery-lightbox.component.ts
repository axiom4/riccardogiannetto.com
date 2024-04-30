import { Component, HostListener, Input, OnInit } from '@angular/core';
import { Item } from '../../models/item';
import {
  animate,
  style,
  transition,
  trigger,
  AnimationEvent,
} from '@angular/animations';
import { NgFor, NgIf } from '@angular/common';
import { GalleryService } from '../../gallery.service';

@Component({
  selector: 'app-gallery-lightbox',
  standalone: true,
  imports: [NgFor, NgIf],
  templateUrl: './gallery-lightbox.component.html',
  styleUrl: './gallery-lightbox.component.scss',
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
export class GalleryLightboxComponent implements OnInit {
  @Input() galleryData: Item[] = [];
  @Input() showCount = false;
  isLoading = false;
  data: Item[] = [];
  page = 1;
  perPage = 25;

  @HostListener('window:scroll', ['$event'])
  onWindowScroll(event: any) {
    if (
      window.innerHeight + window.scrollY >= document.body.offsetHeight - 100 &&
      !this.isLoading
    ) {
      console.log(event);
      this.loadItems();
    }
  }

  previewImage = false;
  showMask = false;
  currentLightboxImg: Item = this.data[0];
  currentIndex = 0;
  controls = true;
  totalImageCount = 0;

  constructor(private galleryService: GalleryService) {}

  ngOnInit(): void {
    this.totalImageCount = this.galleryData.length;
    // this.data = this.galleryData;
    this.loadItems();
  }

  onPreviewImage(index: number): void {
    console.log('Preview image', index);

    this.showMask = true;
    this.previewImage = true;

    this.currentIndex = index;
    this.currentLightboxImg = this.data[index];
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
      this.currentIndex = this.data.length - 1;
    }
    this.currentLightboxImg = this.data[this.currentIndex];
  }

  next(): void {
    this.currentIndex++;
    if (this.currentIndex > this.data.length - 1) {
      this.loadItems();
    } else {
      this.currentLightboxImg = this.data[this.currentIndex];
    }
  }

  loadItems(): void {
    console.log('Load more items');
    this.isLoading = true;
    this.galleryService.getItems(this.page, this.perPage).subscribe((items) => {
      items.photos.forEach((item: any) => {
        const g_item: Item = {
          src: item.src.large,
          alt: item.alt,
        };
        this.data.push(g_item);
      });
      // this.items.push(...items.photos);
      this.page++;
      this.totalImageCount = this.data.length;
      this.isLoading = false;
    });
  }
}
