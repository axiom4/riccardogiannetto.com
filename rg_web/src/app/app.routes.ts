import { Routes } from '@angular/router';

export const routes: Routes = [
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
    path: '',
    // pathMatch: 'full',
    loadChildren: () =>
      import('./modules/main/main.routes').then((m) => m.MAIN_ROUTES),
  },
  {
    path: '**',
    pathMatch: 'full',
    redirectTo: '/',
  },
];
