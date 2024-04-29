import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GalleryLightboxComponent } from './components/gallery-lightbox/gallery-lightbox.component';

@NgModule({
  declarations: [GalleryLightboxComponent],
  exports: [GalleryLightboxComponent],
  imports: [CommonModule],
})
export class GalleryModule {}
