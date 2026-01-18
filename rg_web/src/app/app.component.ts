import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HeaderComponent } from './modules/main/components/header/header.component';
import { FooterComponent } from './modules/main/components/footer/footer.component';
import { CookieBannerComponent } from './components/cookie-banner/cookie-banner.component';

@Component({
    selector: 'app-root',
    imports: [RouterOutlet, HeaderComponent, FooterComponent, CookieBannerComponent],
    templateUrl: './app.component.html',
    styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'Riccardo Giannetto Gallery';
  constructor() {}
}
