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
      document.fonts.load('1em myfantasy').then(() => {
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
