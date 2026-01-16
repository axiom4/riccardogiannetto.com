import { Routes } from '@angular/router';
import { MainPageComponent } from './components/main-page/main-page.component';
import { PageNotFoundComponent } from './components/page-not-found/page-not-found.component';

export const MAIN_ROUTES: Routes = [
  {
    path: '',
    pathMatch: 'full',
    component: MainPageComponent,
  },
  {
    path: 'notfound',
    component: PageNotFoundComponent,
  },
];
