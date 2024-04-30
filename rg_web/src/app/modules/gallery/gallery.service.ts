import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, delay } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class GalleryService {
  pendingReq: boolean = false;
  apiUrl: string = 'https://api.pexels.com/v1/curated';

  constructor(private http: HttpClient) {}

  getItems(page: number, perPage: number) {
    if (this.pendingReq) {
      return {} as Observable<{}>;
    }
    this.pendingReq = true;
    const url = `${this.apiUrl}?per_page=${perPage}&page=${page}`;
    this.pendingReq = false;
    return this.http.get<any>(url).pipe(delay(300));
  }
}
