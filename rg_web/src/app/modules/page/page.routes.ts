import { Routes } from '@angular/router';
import { PageComponent } from './components/page/page.component';

export const PAGE_ROUTES: Routes = [
  { path: '', pathMatch: 'full', redirectTo: '/404' },
  { path: ':tag', component: PageComponent },
];
