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
  fontsLoaded = signal(false);
  private platformId = inject(PLATFORM_ID);

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      // Safety timeout: always show after 2 seconds even if font fails
      const safetyTimeout = setTimeout(() => this.fontsLoaded.set(true), 2000);

      // Check if already loaded
      if (document.fonts.check('1em myfantasy')) {
        clearTimeout(safetyTimeout);
        this.fontsLoaded.set(true);
        return;
      }

      // Wait for load
      document.fonts
        .load('1em myfantasy')
        .then(() => {
          clearTimeout(safetyTimeout);
          this.fontsLoaded.set(true);
        })
        .catch(() => {
          // If error, show anyway
          this.fontsLoaded.set(true);
        });
    } else {
      // In SSR we can't verify, but we can default to true to avoid empty header
      this.fontsLoaded.set(true);
    }
  }

  toggleMenu() {
    console.log('toggle menu');
    this.menu()?.nativeElement.classList.toggle('visible');
  }
}
