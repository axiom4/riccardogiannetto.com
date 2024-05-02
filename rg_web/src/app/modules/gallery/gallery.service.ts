import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, delay, of } from 'rxjs';
import { Item } from './models/item';

@Injectable({
  providedIn: 'root',
})
export class GalleryService {
  pendingReq: boolean = false;
  data: Item[] = [
    {
      src: 'assets/images/1.jpg',
      alt: '1',
      width: 300,
      height: 200,
    },
    {
      src: 'assets/images/2.jpg',
      alt: '2',
      width: 300,
      height: 200,
    },
    {
      src: 'assets/images/3.jpg',
      alt: '3',
      width: 300,
      height: 200,
    },
    {
      src: 'assets/images/4.jpg',
      alt: '4',
      width: 300,
      height: 200,
    },
    {
      src: 'assets/images/5.jpg',
      alt: '5',
      width: 300,
      height: 200,
    },
    {
      src: 'assets/images/6.jpg',
      alt: '6',
      width: 488,
      height: 291,
    },
    {
      src: 'assets/images/7.jpg',
      alt: '7',
      width: 464,
      height: 290,
    },
    {
      src: 'assets/images/8.jpg',
      alt: '8',
      width: 300,
      height: 200,
    },
    {
      src: 'assets/images/9.jpg',
      alt: '9',
      width: 387,
      height: 291,
    },
    {
      src: 'assets/images/10.jpg',
      alt: '10',
      width: 194,
      height: 291,
    },
    {
      src: 'assets/images/11.jpg',
      alt: '11',
      width: 233,
      height: 291,
    },
    {
      src: 'assets/images/12.jpg',
      alt: '12',
      width: 300,
      height: 200,
    },
    {
      src: 'assets/images/13.jpg',
      alt: '13',
      width: 516,
      height: 291,
    },
  ];
  apiUrl: string = 'https://api.pexels.com/v1/curated';

  constructor(private http: HttpClient) {}

  getItems(page: number, perPage: number): Observable<Item[]> {
    if (this.pendingReq) {
      return {} as Observable<Item[]>;
    }
    return of(this.data).pipe(delay(150));
  }
}
