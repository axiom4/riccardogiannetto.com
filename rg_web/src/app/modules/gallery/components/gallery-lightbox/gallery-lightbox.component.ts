import {
  Component,
  ElementRef,
  HostListener,
  Input,
  OnInit,
  QueryList,
  ViewChild,
  ViewChildren,
  afterNextRender,
} from '@angular/core';
import { Item } from '../../models/item';
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
import { GalleryService } from '../../gallery.service';
import { ImageLazyLoaderDirective } from '../../image-lazy-loader.directive';

const myCustomLoader = (config: ImageLoaderConfig) => {
  let url = `${config.src}?`;
  let queryParams = [];
  if (config.width) {
    queryParams.push(`w=${config.width}`);
  }
  return url + queryParams.join('&');
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
      useValue: myCustomLoader,
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
  @Input() galleryData: Item[] = [];
  @Input() showCount = false;
  isLoading = false;
  data: Item[][] = [];
  page = 1;
  perPage = 25;
  innerWidth = 0;
  index = 0;

  columns = 0;

  previewImage = false;
  showMask = false;
  currentLightboxImg: Item | undefined;
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
      this.loadItems();
    }
  }

  @HostListener('document:keydown.escape', ['$event']) onKeydownHandler(
    event: KeyboardEvent
  ) {
    console.log(event);
    if (this.previewImage) {
      this.previewImage = false;
    }
  }

  @HostListener('window:resize', ['$event'])
  onResize(event: any) {
    if (this.innerWidth !== window?.innerWidth) {
      this.innerWidth = window.innerWidth;
      this.setColumns(this.innerWidth);

      if (this.data.length != this.columns && !this.isLoading) this.loadItems();
    }
  }

  constructor(private galleryService: GalleryService) {
    afterNextRender(() => {
      this.innerWidth = window.innerWidth;
      this.setColumns(this.innerWidth);
    });
  }

  ngOnInit(): void {
    this.totalImageCount = 0;
    // this.data = this.galleryData;
    this.loadItems();
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

    this.galleryService
      .getItems(this.page, this.perPage)
      .subscribe((items: Item[]) => {
        if (this.data.length != this.columns) {
          this.data = [];

          for (let i = 0; i < this.columns; i++) {
            this.data.push(new Array<Item>());
          }
        }
        this.index = this.getLowerColumnHeightIndex();

        items.forEach((item: Item) => {
          const g_item: Item = item;
          if (this.data[this.index] != undefined) {
            this.data[this.index].push(g_item);
            this.index = (this.index + 1) % this.columns;
          }
        });

        this.page++;
        let imageCount = 0;
        this.data.forEach((column) => {
          imageCount += column.length;
        });
        this.totalImageCount = imageCount;

        this.isLoading = false;
      });
  }

  setColumns(width: number): void {
    if (width < 650) {
      this.columns = 1;
    } else if (width < 1024) {
      this.columns = 2;
    } else {
      this.columns = 3;
    }
  }

  getLowerColumnHeightIndex(): number {
    let index = 0;
    if (this.galleryItem == undefined) return index;

    if (this.galleryItem.length > 0) {
      let minHeight = this.galleryItem.first.nativeElement.offsetHeight;

      this.galleryItem?.forEach((item) => {
        if (minHeight > item.nativeElement.offsetHeight) {
          minHeight = item.nativeElement.offsetHeight;
          index = this.galleryItem?.toArray().indexOf(item) || 0;
        }
      });
    }
    return index;
  }
}
