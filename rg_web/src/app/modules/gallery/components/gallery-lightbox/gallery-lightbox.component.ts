import {
  Component,
  ElementRef,
  HostListener,
  Input,
  OnInit,
  QueryList,
  ViewChildren,
  afterNextRender,
} from '@angular/core';
import {
  animate,
  style,
  transition,
  trigger,
  AnimationEvent,
} from '@angular/animations';
import {
  IMAGE_LOADER,
  ImageLoaderConfig,
  NgFor,
  NgIf,
  NgOptimizedImage,
} from '@angular/common';
import { ImageLazyLoaderDirective } from '../../image-lazy-loader.directive';
import {
  ImageGallery,
  ListImageGalleriesRequestParams,
  PortfolioService,
} from '../../../core/api/v1';

const galleryLoaderProvider = (config: ImageLoaderConfig) => {
  return `${config.src}`;
};

@Component({
  selector: 'app-gallery-lightbox',
  standalone: true,
  imports: [NgFor, NgIf, ImageLazyLoaderDirective, NgOptimizedImage],
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
  isLoading = false;
  data: ImageGallery[][] = [];
  page = 1;
  perPage = 9;
  innerWidth = 0;
  innerHeight = 0;
  imageWidth = 0;
  index = 0;

  columns = 0;

  previewImage = false;
  showMask = false;
  currentLightboxImg: ImageGallery | undefined;
  currentRow = 0;
  currentColumn = 0;
  controls = true;
  totalImageCount = 0;

  @ViewChildren('galleryItem') galleryItem: QueryList<ElementRef> | undefined;

  @HostListener('window:scroll', ['$event'])
  onWindowScroll(event: any) {
    if (
      window.innerHeight + window.scrollY >= document.body.offsetHeight - 100 &&
      !this.isLoading
    ) {
      let imageCount = 0;

      this.data.forEach((column) => {
        imageCount += column.length;
      });

      if (imageCount < this.totalImageCount) {
        this.loadItems();
      }
    }
  }

  @HostListener('document:keydown.escape', ['$event']) onKeydownHandler(
    event: KeyboardEvent
  ) {
    if (this.previewImage) {
      this.previewImage = false;
    }
  }

  @HostListener('window:resize', ['$event'])
  onResize(event: any) {
    if (this.innerWidth !== window?.innerWidth) {
      this.innerWidth = window.innerWidth;
      this.setColumns(this.innerWidth);

      if (this.data.length != this.columns && !this.isLoading) {
        this.page = 1;
        this.loadItems();
      }
    }
  }

  constructor(private portfolioService: PortfolioService) {
    afterNextRender(() => {
      this.innerWidth = window.innerWidth;
      this.innerHeight = window.innerHeight;

      this.setColumns(this.innerWidth);
      this.loadItems();
    });
  }

  ngOnInit(): void {
    this.totalImageCount = 0;
  }

  onPreviewImage(column: number, row: number): void {
    this.showMask = true;
    this.previewImage = true;

    this.currentRow = row;
    this.currentColumn = column;

    this.currentLightboxImg = this.data[column][row];
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
    this.currentRow--;
    if (this.currentRow < 0) {
      if (this.currentColumn == 0) {
        this.currentColumn = this.columns - 1;
      } else {
        this.currentColumn = (this.currentColumn - 1) % this.columns;
      }
      this.currentRow = this.data[this.currentColumn].length - 1;
    }
    this.currentLightboxImg = this.data[this.currentColumn][this.currentRow];
  }

  next(): void {
    this.currentRow++;
    if (this.currentRow > this.data[this.currentColumn].length - 1) {
      this.currentRow = 0;
      this.currentColumn = (this.currentColumn + 1) % this.columns;
    }
    this.currentLightboxImg = this.data[this.currentColumn][this.currentRow];
  }

  loadItems(): void {
    this.isLoading = true;
    const params: ListImageGalleriesRequestParams = {
      gallery: '1',
      page: this.page,
      pageSize: this.perPage,
    };
    this.portfolioService.listImageGalleries(params).subscribe((data) => {
      if (this.data.length != this.columns) {
        this.data = [];

        for (let i = 0; i < this.columns; i++) {
          this.data.push(new Array<ImageGallery>());
        }
      }

      const items = data.results;

      items.forEach((item: ImageGallery) => {
        const index = this.getLowerColumnHeightIndex();

        if (this.data[index] != undefined) {
          this.data[index].push(item);
        }
      });

      this.page++;
      this.totalImageCount = data.count;

      this.isLoading = false;
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

  getLowerColumnHeightIndex(): number {
    let index = 0;
    if (this.galleryItem == undefined) return index;

    for (let i = 0; i < this.columns; i++) {
      if (this.getColumnHeight(i) < this.getColumnHeight(index)) {
        index = i;
      }
    }

    console.log('selected index', index);
    return index;
  }

  getColumnHeight(index: number): number {
    let height = 0;

    this.data[index].forEach((item) => {
      height += item.height / item.width;
    });

    console.log(index, height);
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
      return Math.floor(this.innerWidth * 0.8);
    }
    return Math.floor(
      (imageWidth / imageHeight) * Math.floor(this.innerHeight * 0.9)
    );
  }

  getGalleryImageHeight(imageWidth: number, imageHeight: number): number {
    if (imageHeight < imageWidth) {
      return Math.floor(
        (imageHeight / imageWidth) * Math.floor(this.innerWidth * 0.8)
      );
    }
    return Math.floor(this.innerHeight * 0.9);
  }
}
