import { Routes } from '@angular/router';
import { MainPageComponent } from './modules/main/components/main-page/main-page.component';
import { PageNotFoundComponent } from './modules/main/components/page-not-found/page-not-found.component';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    component: MainPageComponent,
  },
  {
    path: 'notfound',
    component: PageNotFoundComponent,
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
    path: '**',
    pathMatch: 'full',
    redirectTo: '/',
  },
];
