import { AfterViewInit, Directive, ElementRef, HostListener, Renderer2, inject } from '@angular/core';

@Directive({
  selector: 'img[appImageLazyLoader]',
  standalone: true,
})
export class ImageLazyLoaderDirective implements AfterViewInit {
  private renderer = inject(Renderer2);
  private el = inject(ElementRef);

  // @HostBinding('attr.src') srcAttr: string | undefined;
  // @Input() src: string | undefined;

  private _loading = true;
  private _error = false;

  get error(): boolean {
    return this._error;
  }

  get loading(): boolean {
    return this._loading;
  }
  set loading(val: boolean) {
    if (val) this.renderer.addClass(this.el.nativeElement, 'loading');
    else this.renderer.removeClass(this.el.nativeElement, 'loading');
    this._loading = val;
  }

  @HostListener('loadstart') onLoadStart() {
    this.loading = true;
  }

  @HostListener('load') onLoad() {
    this.loading = false;
    this.renderer.addClass(this.el.nativeElement, 'loaded');
  }
  @HostListener('error') onError() {
    this.loading = false;
    this._error = true;
    this.renderer.addClass(this.el.nativeElement, 'error');
  }

  // private canLazyLoad() {
  //   return window && 'IntersectionObserver' in window;
  // }

  // private lazyLoadImage() {
  //   const obs = new IntersectionObserver((entries) => {
  //     entries.forEach(({ isIntersecting }) => {
  //       if (isIntersecting) {
  //         this.loadImage();
  //         obs.unobserve(this.el.nativeElement);
  //       }
  //     });
  //   });
  //   obs.observe(this.el.nativeElement);
  // }

  // private loadImage() {
  //   this.srcAttr = this.src;
  // }
}
