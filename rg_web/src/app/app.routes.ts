import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    loadComponent: () =>
      import(
        './modules/main/components/main-page/main-page.component'
      ).then((m) => m.MainPageComponent),
  },
  {
    path: 'notfound',
    loadComponent: () =>
      import(
        './modules/main/components/page-not-found/page-not-found.component'
      ).then((m) => m.PageNotFoundComponent),
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
