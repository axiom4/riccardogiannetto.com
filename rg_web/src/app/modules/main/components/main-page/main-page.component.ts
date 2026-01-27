import { Component, ChangeDetectionStrategy } from '@angular/core';
import { GalleryLightboxComponent } from '../../../gallery/components/gallery-lightbox/gallery-lightbox.component';

@Component({
  selector: 'app-main-page',
  imports: [GalleryLightboxComponent],
  templateUrl: './main-page.component.html',
  styleUrl: './main-page.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MainPageComponent {}
