import {
  Directive,
  ElementRef,
  HostListener,
  Renderer2,
  inject,
} from '@angular/core';

@Directive({
  selector: 'img[appImageLazyLoader]',
  standalone: true,
})
export class ImageLazyLoaderDirective {
  private renderer = inject(Renderer2);
  private el = inject(ElementRef);

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
}
