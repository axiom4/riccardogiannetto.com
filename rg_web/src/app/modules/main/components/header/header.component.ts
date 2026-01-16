import { Component, ElementRef, viewChild } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-header',
  imports: [RouterLink],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss',
})
export class HeaderComponent {
  menu = viewChild<ElementRef>('menu');
  toggleMenu() {
    console.log('toggle menu');
    this.menu()?.nativeElement.classList.toggle('visible');
  }
}
