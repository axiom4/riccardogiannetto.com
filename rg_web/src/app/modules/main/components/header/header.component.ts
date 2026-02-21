import {
  Component,
  ElementRef,
  inject,
  OnInit,
  PLATFORM_ID,
  signal,
  viewChild,
  ChangeDetectionStrategy,
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-header',
  imports: [RouterLink],
  templateUrl: './header.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HeaderComponent implements OnInit {
  menu = viewChild<ElementRef>('menu');
  isLoaded = signal(false);
  private platformId = inject(PLATFORM_ID);

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      // Wait for fonts to be ready to avoid FOUC (Flash of Unstyled Content)
      // especially for the SVG logo which uses a custom font
      document.fonts.ready.then(() => {
        this.isLoaded.set(true);
      });
    } else {
      this.isLoaded.set(true);
    }
  }

  toggleMenu() {
    this.menu()?.nativeElement.classList.toggle('visible');
  }
}
