import { Component, ViewChild } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss',
})
export class HeaderComponent {
  @ViewChild('menu') menu: any;
  toggleMenu() {
    console.log('toggle menu');
    this.menu.nativeElement.classList.toggle('visible');
  }
}
