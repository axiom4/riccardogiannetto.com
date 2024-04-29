import { Component } from '@angular/core';
import { Item } from '../../gallery/models/item';
import { GalleryModule } from '../../gallery/gallery.module';
import { GalleryLightboxComponent } from '../../gallery/components/gallery-lightbox/gallery-lightbox.component';

@Component({
  selector: 'app-main-page',
  standalone: true,
  imports: [GalleryLightboxComponent],
  templateUrl: './main-page.component.html',
  styleUrl: './main-page.component.scss',
})
export class MainPageComponent {
  data: Item[] = [
    {
      src: 'assets/images/1.jpg',
      alt: '1',
    },
    {
      src: 'assets/images/2.jpg',
      alt: '2',
    },
    {
      src: 'assets/images/3.jpg',
      alt: '3',
    },
    {
      src: 'assets/images/4.jpg',
      alt: '4',
    },
    {
      src: 'assets/images/5.jpg',
      alt: '5',
    },
    {
      src: 'assets/images/6.jpg',
      alt: '6',
    },
    {
      src: 'assets/images/7.jpg',
      alt: '7',
    },
    {
      src: 'assets/images/8.jpg',
      alt: '8',
    },
    {
      src: 'assets/images/9.jpg',
      alt: '9',
    },
    {
      src: 'assets/images/10.jpg',
      alt: '10',
    },
    {
      src: 'assets/images/11.jpg',
      alt: '11',
    },
    {
      src: 'assets/images/12.jpg',
      alt: '12',
    },
    {
      src: 'assets/images/13.jpg',
      alt: '13',
    },
  ];
}
