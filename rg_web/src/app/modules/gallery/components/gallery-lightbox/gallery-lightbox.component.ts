import {
  Component,
  ElementRef,
  HostListener,
  inject,
  OnInit,
  QueryList,
  signal,
  viewChildren,
} from '@angular/core';
import {
  animate,
  style,
  transition,
  trigger,
  AnimationEvent,
} from '@angular/animations';
import { IMAGE_LOADER, ImageLoaderConfig } from '@angular/common';
import {
  ImageGallery,
  PortfolioImagesListRequestParams,
  PortfolioService,
} from '../../../core/api/v1';

const galleryLoaderProvider = (config: ImageLoaderConfig) => {
  return `${config.src}`;
};

@Component({
  selector: 'app-gallery-lightbox',
  imports: [],
  templateUrl: './gallery-lightbox.component.html',
  styleUrl: './gallery-lightbox.component.scss',
  providers: [
    {
      provide: IMAGE_LOADER,
      useValue: galleryLoaderProvider,
    },
  ],
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
  private portfolioService = inject(PortfolioService);

  isLoading = signal(false);
  data = signal<ImageGallery[][]>([]);
  page = signal(1);
  perPage = 9;
  innerWidth = 0;
  innerHeight = 0;
  imageWidth = signal(0);
  index = 0;

  columns = 0;

  previewImage = signal(false);
  showMask = signal(false);
  currentLightboxImg = signal<ImageGallery | undefined>(undefined);
  currentRow = 0;
  currentColumn = 0;
  controls = true;

  totalImageCount = 0;
  imageNum = 0;

  galleryItem = viewChildren<ElementRef>('galleryItem');

  @HostListener('window:scroll', ['$event'])
  onWindowScroll(event: any) {
    if (
      window.innerHeight + window.scrollY >= document.body.offsetHeight - 100 &&
      !this.isLoading()
    ) {
      let imageCount = 0;

      this.data().forEach((column) => {
        imageCount += column.length;
      });

      if (imageCount < this.totalImageCount) {
        this.loadItems();
      }
    }
  }

  @HostListener('document:keydown.escape', ['$event']) onKeydownEscapeHandler(
    event: Event
  ) {
    if (this.previewImage()) {
      this.previewImage.set(false);
    }
  }

  @HostListener('document:keydown.arrowLeft', ['$event']) onKeydownLeftHandler(
    event: Event
  ) {
    if (this.previewImage()) {
      this.prev();
    }
  }

  @HostListener('document:keydown.arrowRight', ['$event'])
  onKeydownRighttHandler(event: Event) {
    if (this.previewImage()) {
      this.next();
    }
  }

  @HostListener('window:resize', ['$event'])
  onResize(event: any) {
    if (this.innerWidth !== window?.innerWidth) {
      this.innerWidth = window.innerWidth;
      this.setColumns(this.innerWidth);

      if (this.data().length != this.columns && !this.isLoading()) {
        this.page.set(1);
        this.loadItems();
      }
    }
  }

  constructor() {}

  ngOnInit(): void {
    this.totalImageCount = 0;
    this.innerWidth = window.innerWidth;
    this.innerHeight = window.innerHeight;

    this.setColumns(this.innerWidth);
    this.loadItems();
  }

  onPreviewImage(column: number, row: number): void {
    this.showMask.set(true);
    this.previewImage.set(true);

    this.currentRow = row;
    this.currentColumn = column;

    this.currentLightboxImg.set(this.data()[column][row]);
  }

  onAnimationEnd(event: AnimationEvent): void {
    if (event.toState === 'void') {
      this.showMask.set(false);
      this.previewImage.set(false);
    }
  }

  onclosePreview(): void {
    this.previewImage.set(false);
  }

  prev(): void {
    this.currentRow--;
    if (this.currentRow < 0) {
      if (this.currentColumn == 0) {
        this.currentColumn = this.columns - 1;
      } else {
        this.currentColumn = (this.currentColumn - 1) % this.columns;
      }
      this.currentRow = this.data()[this.currentColumn].length - 1;
    }
    this.currentLightboxImg.set(this.data()[this.currentColumn][this.currentRow]);
  }

  next(): void {
    this.currentRow++;
    if (this.currentRow > this.data()[this.currentColumn].length - 1) {
      this.currentRow = 0;
      this.currentColumn = (this.currentColumn + 1) % this.columns;
    }
    this.currentLightboxImg.set(this.data()[this.currentColumn][this.currentRow]);
  }

  loadItems(): void {
    this.isLoading.set(true);
    const params: PortfolioImagesListRequestParams = {
      gallery: 1,
      page: this.page(),
      pageSize: this.perPage,
      ordering: '-date',
    };
    this.portfolioService.portfolioImagesList(params).subscribe((data) => {
      let workingData: ImageGallery[][] = [];

      // Initialize or clone data
      const currentData = this.data();
      if (currentData.length !== this.columns) {
        for (let i = 0; i < this.columns; i++) {
          workingData.push([]);
        }
      } else {
        // Create a deep copy to ensure new references for change detection
        workingData = currentData.map(col => [...col]);
      }

      const items = data.results;

      items.forEach((item: ImageGallery) => {
        // Pass workingData so we calculate height based on the current batch state
        const index = this.getLowerColumnHeightIndex(workingData);

        if (workingData[index] != undefined) {
          workingData[index].push(item);
        }
      });
      
      this.data.set(workingData);

      this.page.update(p => p + 1);
      this.totalImageCount = data.count;

      this.isLoading.set(false);
    });
  }

  setColumns(width: number): void {
    if (width < 650) {
      this.columns = 1;
      this.perPage = 5;
    } else if (width < 1024) {
      this.columns = 2;
      this.perPage = 8;
    } else {
      this.columns = 3;
      this.perPage = 9;
    }
  }

  getLowerColumnHeightIndex(data: ImageGallery[][]): number {
    let index = 0;
    // Because viewChildren is a signal, we access it like a function
    const galleryItems = this.galleryItem();
    if (galleryItems.length == 0 && data.flat().length > 0) {
         // If ViewChildren not ready but we have data, we might default to 0
         // or if it's the very first load.
         // However, logic relies on assumption columns exist.
    }

    for (let i = 0; i < this.columns; i++) {
      if (this.getColumnHeight(i, data) < this.getColumnHeight(index, data)) {
        index = i;
      }
    }

    return index;
  }

  getColumnHeight(index: number, data: ImageGallery[][]): number {
    let height = 0;
    
    // Check if column exists in the provided data
    if(data[index]) {
        data[index].forEach((item) => {
            height += item.height / item.width;
        });
    }

    return height;
  }

  getGalleryPreviewWidth(): number {
    if (this.columns == 3) {
      return 700;
    } else if (this.columns == 2) {
      return 1000;
    }
    return 1200;
  }

  getGalleryPreviewHeight(imageWidth: number, imageHeight: number): number {
    if (this.columns == 3) {
      return Math.floor((imageHeight / imageWidth) * 700);
    } else if (this.columns == 2) {
      return Math.floor((imageHeight / imageWidth) * 1000);
    }
    return Math.floor((imageHeight / imageWidth) * 1200);
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
