import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MainModule } from './modules/main/main.module';
import { HeaderComponent } from './modules/main/components/header/header.component';
import { FooterComponent } from './modules/main/components/footer/footer.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, HeaderComponent, FooterComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  title = 'Riccardo Giannetto Gallery';
}
