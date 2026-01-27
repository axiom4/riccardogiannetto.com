import {
  Component,
  effect,
  ElementRef,
  HostListener,
  inject,
  OnDestroy,
  OnInit,
  signal,
  viewChild,
  viewChildren,
  afterNextRender,
  ChangeDetectionStrategy,
} from '@angular/core';
import { IMAGE_LOADER, ImageLoaderConfig, NgClass } from '@angular/common';
import {
  ImageGallery,
  PortfolioImagesListRequestParams,
  PortfolioService,
} from '../../../core/api/v1';
import { LightboxComponent } from '../lightbox/lightbox.component';

const galleryLoaderProvider = (config: ImageLoaderConfig) => {
  return `${config.src}`;
};

export interface GalleryItem {
  data: ImageGallery;
  cols: number;
  rows: number;
  baseCols: number;
  baseRows: number;
  gridColumnStart?: number;
  gridRowStart?: number;
  isLoading: boolean;
}

@Component({
  selector: 'app-gallery-lightbox',
  imports: [NgClass, LightboxComponent],
  templateUrl: './gallery-lightbox.component.html',
  styleUrl: './gallery-lightbox.component.scss',
  providers: [
    {
      provide: IMAGE_LOADER,
      useValue: galleryLoaderProvider,
    },
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class GalleryLightboxComponent implements OnInit, OnDestroy {
  private portfolioService = inject(PortfolioService);

  isLoading = signal(false);
  galleryItems = signal<GalleryItem[]>([]);
  page = signal(1);
  perPage = 4;
  innerWidth = 0;
  innerHeight = 0;
  imageWidth = signal(0);
  index = 0;

  columns = 1;

  previewImage = signal(false);
  showMask = signal(false);
  currentLightboxImg = signal<ImageGallery | undefined>(undefined);
  currentIdx = 0;
  controls = true;

  totalImageCount = 0;
  hasNextPage = true;
  imageNum = 0;
  pageFlipDirection = signal<'next' | 'prev'>('next');

  private lastItemWasLarge = false;

  // Layout State for incremental updates
  private colHeights: number[] = [0];
  private processedCount = 0;
  private preferRightSide = false;

  galleryItem = viewChildren<ElementRef>('galleryItem');
  sentinel = viewChild<ElementRef>('sentinel');
  private observer: IntersectionObserver | undefined;
  private isSentinelIntersecting = false;

  constructor() {
    afterNextRender(() => {
      this.innerWidth = window.innerWidth;
      this.innerHeight = window.innerHeight;
      this.setColumns(this.innerWidth);
      if (this.galleryItems().length > 0) {
        this.recalculateLayout();
      }
    });

    effect(() => {
      const el = this.sentinel();
      if (el) {
        this.setupObserver(el.nativeElement);
      }
    });
  }

  ngOnDestroy(): void {
    this.observer?.disconnect();
  }

  setupObserver(target: Element) {
    this.observer?.disconnect();

    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          this.isSentinelIntersecting = entry.isIntersecting;
          if (entry.isIntersecting && !this.isLoading() && this.hasNextPage) {
            this.loadItems();
          }
        });
      },
      {
        root: null,
        rootMargin: '200%',
        threshold: 0.1,
      },
    );

    this.observer.observe(target);
  }

  @HostListener('window:resize')
  onResize() {
    if (this.innerWidth !== window?.innerWidth) {
      this.innerWidth = window.innerWidth;
      this.setColumns(this.innerWidth);
      this.recalculateLayout();
    }
  }

  ngOnInit(): void {
    this.totalImageCount = 0;
    this.loadItems();
  }

  onPreviewImage(index: number): void {
    this.showMask.set(true);
    this.previewImage.set(true);
    this.currentIdx = index;
    this.currentLightboxImg.set(this.galleryItems()[index].data);
    this.imageNum = index + 1;
  }

  onAnimationEnd(): void {
    this.showMask.set(false);
    this.previewImage.set(false);
  }

  onclosePreview(): void {
    this.previewImage.set(false);
  }

  onImageLoad(item: GalleryItem): void {
    item.isLoading = false;
  }

  prev(): void {
    this.pageFlipDirection.set('prev');
    this.currentIdx--;
    if (this.currentIdx < 0) {
      this.currentIdx = this.galleryItems().length - 1;
    }
    this.currentLightboxImg.set(this.galleryItems()[this.currentIdx].data);
    this.imageNum = this.currentIdx + 1;
  }

  next(): void {
    this.pageFlipDirection.set('next');

    // Pre-load next page if we are close to the end
    if (this.hasNextPage && this.currentIdx >= this.galleryItems().length - 3) {
      this.loadItems();
    }

    const nextIdx = this.currentIdx + 1;

    if (nextIdx < this.galleryItems().length) {
      this.currentIdx = nextIdx;
      this.currentLightboxImg.set(this.galleryItems()[this.currentIdx].data);
      this.imageNum = this.currentIdx + 1;
    } else {
      // End of currently loaded items
      if (this.hasNextPage) {
        // Wait for more items to load
        this.loadItems();
      } else {
        // Loop back to start
        this.currentIdx = 0;
        this.currentLightboxImg.set(this.galleryItems()[this.currentIdx].data);
        this.imageNum = this.currentIdx + 1;
      }
    }
  }

  loadItems(): void {
    if (!this.hasNextPage || this.isLoading()) return;
    this.isLoading.set(true);
    const params: PortfolioImagesListRequestParams = {
      gallery: 1,
      page: this.page(),
      pageSize: this.perPage,
      ordering: '-date,-id',
    };
    this.portfolioService.portfolioImagesList(params).subscribe((data) => {
      const newItems: GalleryItem[] = data.results.map((img: ImageGallery) => {
        const isPortrait = img.height > img.width;
        let cols = 1;
        let rows = 1;

        if (isPortrait) {
          rows = 2;
        }

        // Randomly (20% chance) make it big, BUT only if previous wasn't large
        if (!this.lastItemWasLarge && Math.random() > 0.8) {
          if (!isPortrait) {
            // Landscape -> 2x2
            cols = 2;
            rows = 2;
          } else {
            // Portrait -> 2 columns, 4 rows
            cols = 2;
            rows = 4;
          }
          this.lastItemWasLarge = true;
        } else {
          this.lastItemWasLarge = false;
        }

        return {
          data: img,
          cols,
          rows,
          baseCols: cols,
          baseRows: rows,
          isLoading: true,
        };
      });

      this.galleryItems.update((items) => {
        const existingUrls = new Set(items.map((i) => i.data.url));
        const filteredNewItems = [];

        for (const newItem of newItems) {
          if (!existingUrls.has(newItem.data.url)) {
            filteredNewItems.push(newItem);
            existingUrls.add(newItem.data.url);
          }
        }

        const updated = [...items, ...filteredNewItems];
        // We will layout in the next step, but update state first
        return updated;
      });

      this.recalculateLayout();

      this.page.update((p) => p + 1);
      this.totalImageCount = data.count;
      this.hasNextPage = !!data.next;

      this.isLoading.set(false);

      // If sentinel is strictly still visible after load, trigger next load immediately
      // This replaces the old scrollHeight calculation with a passive check
      if (this.isSentinelIntersecting && this.hasNextPage) {
        // Use a microtask or small timeout to let the DOM update first
        setTimeout(() => {
          if (this.isSentinelIntersecting) {
            this.loadItems();
          }
        }, 0);
      }
    });
  }

  recalculateLayout(): void {
    const allItems = this.galleryItems();

    // Safety: If we have fewer items than processed (reset?), reset state
    if (allItems.length < this.processedCount) {
      this.processedCount = 0;
      this.colHeights = new Array(this.columns).fill(0);
      this.preferRightSide = false;
    }

    if (this.processedCount >= allItems.length) return;

    const colHeights = this.colHeights;
    const placedItems = allItems.slice(0, this.processedCount);

    const items = allItems.slice(this.processedCount).map((it) => ({
      ...it,
      cols: it.baseCols,
      rows: it.baseRows,
    }));

    if (!items.length) return;

    // Helper to keep code below happy with local var, syncing to class prop
    let preferRightSide = this.preferRightSide;

    const getEffectiveSize = (item: GalleryItem) => {
      let eCols = item.baseCols;
      let eRows = item.baseRows;

      if (this.columns === 1) {
        eCols = 1;
        // Adjust height for single column mobile view
        if (item.baseCols === 2 && item.baseRows === 2) eRows = 1;
        if (item.baseCols === 2 && item.baseRows === 4) eRows = 2;
      } else if (this.columns === 2) {
        if (eCols > 2) eCols = 2;
      }
      return { eCols, eRows };
    };

    let attempts = 0;
    // Safety break to prevent infinite loops, though unlikely with splice
    while (items.length > 0 && attempts < items.length * 2 + 100) {
      attempts++;

      // 1. Find the lowest slot (Min-Height Strategy)
      const minH = Math.min(...colHeights);

      let startCol = -1;
      let availableWidth = 0;

      for (let c = 0; c < this.columns; c++) {
        if (colHeights[c] === minH) {
          // Measure shelf width
          let w = 0;
          for (let k = c; k < this.columns; k++) {
            if (colHeights[k] === minH) w++;
            else break;
          }
          if (w > availableWidth) {
            availableWidth = w;
            startCol = c;
          }
        }
      }

      // Calculate context bounds for "Flatness" strategy
      // We check neighboring columns to define a "ceiling" we shouldn't exceed
      const leftH = startCol > 0 ? colHeights[startCol - 1] : Infinity;
      const rightH =
        startCol + availableWidth < this.columns
          ? colHeights[startCol + availableWidth]
          : Infinity;
      const shelfCeiling = Math.min(leftH, rightH);

      // 3. Search for the best fitting item (among new items only)
      let bestItemIndex = -1;
      let bestItemMetric = -Infinity;

      for (let i = 0; i < items.length; i++) {
        const sz = getEffectiveSize(items[i]);

        // Constraint: No vertical overlap with existing large items
        let conflict = false;
        if (sz.eCols >= 2) {
          const yStart = minH;
          const yEnd = minH + sz.eRows;

          // Check against ALL placed items (old + newly placed in this batch)
          for (const p of placedItems) {
            if (p.cols >= 2) {
              const pStart = (p.gridRowStart || 0) - 1;
              const pEnd = pStart + p.rows;
              if (pStart < yEnd && pEnd > yStart) {
                conflict = true;
                break;
              }
            }
          }
        }

        if (conflict) continue;

        // Constraint 2: No adjancent tall items
        if (sz.eRows >= 2 && sz.eCols === 1) {
          const yStart = minH;
          const yEnd = minH + sz.eRows;
          let validPlacementExists = false;

          for (let offset = 0; offset < availableWidth; offset++) {
            const tryCol = startCol + offset;
            let leftBad = false;
            if (tryCol > 0) {
              leftBad = placedItems.some((p) => {
                if (p.gridColumnStart !== tryCol - 1 + 1) return false;
                if (p.rows < 2) return false;
                const pStart = (p.gridRowStart || 0) - 1;
                const pEnd = pStart + p.rows;
                return pStart < yEnd && pEnd > yStart;
              });
            }
            let rightBad = false;
            if (tryCol < this.columns - 1) {
              rightBad = placedItems.some((p) => {
                if (p.gridColumnStart !== tryCol + 1 + 1) return false;
                if (p.rows < 2) return false;
                const pStart = (p.gridRowStart || 0) - 1;
                const pEnd = pStart + p.rows;
                return pStart < yEnd && pEnd > yStart;
              });
            }
            if (!leftBad && !rightBad) {
              validPlacementExists = true;
              break;
            }
          }
          if (!validPlacementExists) continue;
        }

        if (sz.eCols <= availableWidth) {
          // METRIC IMPROVEMENT: "Flat Top" Strategy.
          // If the item fills the width (eCols >= availableWidth), we target the external shelfCeiling.
          // If the item is narrower (splits the shelf), we are effectively creating a step against our own floor (minH).
          const localCeiling = sz.eCols >= availableWidth ? shelfCeiling : minH;

          // Calculate how much this item would stick out above the desired ceiling
          const overshoot = Math.max(0, minH + sz.eRows - localCeiling);

          // Formula:
          // 1. Width * 1000: Filling width is #1 priority (prevents holes).
          // 2. Rows * 10: Bigger items make more progress.
          // 3. Overshoot * -20: Strict penalty for creating jagged columns. OVERSHOOT > ROW GAIN.
          const metric = sz.eCols * 1000 + sz.eRows * 10 - overshoot * 20;

          if (metric > bestItemMetric) {
            bestItemMetric = metric;
            bestItemIndex = i;
          }
        }
      }

      // 4. Handle "No Item Fits" (The Gap Problem)
      if (bestItemIndex === -1) {
        // Fallback: Pick the first available item and force-shrink it.
        bestItemIndex = 0;

        // Splicing the item out
        const item = items.splice(bestItemIndex, 1)[0];

        // Force dimensions to fit 1xN gap
        let forcedRows = 1;
        if (item.baseCols === 2 && item.baseRows === 4) {
          forcedRows = 2; // squashing 2x4 -> 1x2 to keep some aspect
        }

        item.cols = 1;
        item.rows = forcedRows;

        item.gridColumnStart = startCol + 1;
        item.gridRowStart = minH + 1;

        for (let w = 0; w < item.cols; w++) {
          colHeights[startCol + w] += item.rows;
        }

        placedItems.push(item);
        continue;
      }

      // 5. Place the Item (Natural Fit)
      const item = items.splice(bestItemIndex, 1)[0];

      // Apply natural size
      const naturalSz = getEffectiveSize(item);
      item.cols = naturalSz.eCols;
      item.rows = naturalSz.eRows;

      // Alternating Offset Strategy & Constraint Validation:
      // We must pick an offset (0 to slack) that is VALID (no heavy adjacency collisions).
      let offset = 0;
      const slack = availableWidth - item.cols;

      if (slack > 0) {
        // If 1x2 (Tall, Narrow), we MUST find the valid offset we promised existed in Step 3.
        if (naturalSz.eRows >= 2 && naturalSz.eCols === 1) {
          // Search for the valid offset again
          for (let tryOff = 0; tryOff <= slack; tryOff++) {
            const tryCol = startCol + tryOff;

            // Check Left
            let leftBad = false;
            if (tryCol > 0) {
              leftBad = placedItems.some((p) => {
                if (p.gridColumnStart !== tryCol - 1 + 1) return false;
                if (p.rows < 2) return false;
                const pStart = (p.gridRowStart || 0) - 1;
                const pEnd = pStart + p.rows;
                return pStart < minH + item.rows && pEnd > minH;
              });
            }

            // Check Right
            let rightBad = false;
            if (tryCol < this.columns - 1) {
              rightBad = placedItems.some((p) => {
                if (p.gridColumnStart !== tryCol + 1 + 1) return false;
                if (p.rows < 2) return false;
                const pStart = (p.gridRowStart || 0) - 1;
                const pEnd = pStart + p.rows;
                return pStart < minH + item.rows && pEnd > minH;
              });
            }

            if (!leftBad && !rightBad) {
              offset = tryOff; // Found it!
              break;
            }
          }
        } else {
          // For Wide items (2x2), use the alternating logic (Left/Right preference)
          offset = preferRightSide ? slack : 0;
        }
      }

      const placeCol = startCol + offset;

      // Update alternation state for next time
      // Logic: If we just placed a big item (2 cols) in a multi-col grid (3 or 4 cols)...
      if ((this.columns === 3 || this.columns === 4) && item.cols === 2) {
        // If we placed it on the Left (col 0), next time prefer Right.
        if (placeCol === 0) {
          preferRightSide = true;
        }
        // If we placed it on the Right (offset > 0), next time prefer Left.
        else {
          preferRightSide = false;
        }
      }

      item.gridColumnStart = placeCol + 1;
      item.gridRowStart = minH + 1;

      for (let w = 0; w < item.cols; w++) {
        colHeights[placeCol + w] += item.rows;
      }

      placedItems.push(item);
    }

    this.preferRightSide = preferRightSide;
    this.processedCount = placedItems.length;

    this.galleryItems.set(placedItems);
  }

  setColumns(width: number): void {
    const oldCols = this.columns;

    // Use 4 items per page as requested
    this.perPage = 4;

    if (width < 650) {
      this.columns = 1;
    } else if (width < 1024) {
      this.columns = 2;
    } else if (width < 1500) {
      this.columns = 3;
      // 16 isn't divisible by 3. 15 or 18 would be better for alignment,
      // but '16' was the specific request.
      // Keeping 16.
    } else {
      this.columns = 4;
    }

    // If columns count changed, or we are initializing, reset layout state
    if (oldCols !== this.columns || this.colHeights.length === 0) {
      this.colHeights = new Array(this.columns).fill(0);
      this.processedCount = 0;
      this.preferRightSide = false;
    }
  }

  getGalleryPreviewWidth(): number {
    return 600;
  }

  getGalleryPreviewHeight(imageWidth: number, imageHeight: number): number {
    return Math.floor((imageHeight / imageWidth) * 600);
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
