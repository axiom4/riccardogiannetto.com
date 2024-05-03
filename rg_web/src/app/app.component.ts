import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HeaderComponent } from './modules/main/components/header/header.component';
import { FooterComponent } from './modules/main/components/footer/footer.component';
import {
  PortfolioService,
  RetrieveImageGalleryRequestParams,
} from './modules/core/api/v1';
import { options } from 'marked';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, HeaderComponent, FooterComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent implements OnInit {
  title = 'Riccardo Giannetto Gallery';
  constructor(private portfolioService: PortfolioService) {}

  ngOnInit(): void {
    const params: RetrieveImageGalleryRequestParams = {
      id: '1',
      gallery: '1',
      width: '300',
    };
    this.portfolioService.retrieveImageGallery(params).subscribe((data) => {
      console.log(data);
    });
  }
}
