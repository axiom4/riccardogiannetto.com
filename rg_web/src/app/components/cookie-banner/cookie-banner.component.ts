import { Component, Inject, PLATFORM_ID, OnInit } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-cookie-banner',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './cookie-banner.component.html',
  styleUrl: './cookie-banner.component.scss',
})
export class CookieBannerComponent implements OnInit {
  accepted = true; // Default to true to avoid flash/SSR issues, enable on client check

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {}

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
