import {
  Component,
  ElementRef,
  inject,
  OnInit,
  PLATFORM_ID,
  signal,
  viewChild,
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-header',
  imports: [RouterLink],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss',
})
export class HeaderComponent implements OnInit {
  menu = viewChild<ElementRef>('menu');
  isLoaded = signal(false);
  private platformId = inject(PLATFORM_ID);

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      // Use requestAnimationFrame to ensure we are in the next paint frame after init
      // Or window.onload if strictly "page load" is required, but usually
      // minimal delay after view init is better for SPA feeling.

      // Let's use a small timeout to allow browser to parse SVG/Fonts
      setTimeout(() => {
        this.isLoaded.set(true);
      }, 100);
    } else {
      this.isLoaded.set(true);
    }
  }

  toggleMenu() {
    console.log('toggle menu');
    this.menu()?.nativeElement.classList.toggle('visible');
  }
}
