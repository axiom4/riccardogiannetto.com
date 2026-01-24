import { Component, PLATFORM_ID, OnInit, inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-cookie-banner',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './cookie-banner.component.html',
  styleUrl: './cookie-banner.component.scss',
})
export class CookieBannerComponent implements OnInit {
  private platformId = inject<object>(PLATFORM_ID);

  accepted = true;

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      const consent = localStorage.getItem('cookie_consent');
      this.accepted = consent === 'true';
    }
  }

  accept() {
    this.accepted = true;
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('cookie_consent', 'true');
    }
  }
}
