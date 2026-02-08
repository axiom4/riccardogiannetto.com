import { Routes } from '@angular/router';
import { MainPageComponent } from './modules/main/components/main-page/main-page.component';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    component: MainPageComponent,
  },
  {
    path: 'notfound',
    loadComponent: () =>
      import('./modules/main/components/page-not-found/page-not-found.component').then(
        (m) => m.PageNotFoundComponent,
      ),
  },
  {
    path: 'pages',
    loadChildren: () =>
      import('./modules/page/page.routes').then((m) => m.PAGE_ROUTES),
  },
  {
    path: 'blog',
    loadChildren: () =>
      import('./modules/blog/blog.routes').then((m) => m.BLOG_ROUTES),
  },
  {
    path: 'map',
    loadComponent: () =>
      import('./modules/gallery/components/map/map.component').then(
        (m) => m.MapComponent,
      ),
  },
  {
    path: '**',
    pathMatch: 'full',
    redirectTo: '/',
  },
];
