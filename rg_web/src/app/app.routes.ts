import { Routes } from '@angular/router';
import { MainPageComponent } from './modules/main/components/main-page/main-page.component';
import { PageNotFoundComponent } from './modules/main/components/page-not-found/page-not-found.component';

export const routes: Routes = [
  {
    path: 'pages',
    loadChildren: () =>
      import('./modules/page/page.module').then((m) => m.PageModule),
  },
  {
    path: 'blog',
    loadChildren: () =>
      import('./modules/blog/blog.module').then((m) => m.BlogModule),
  },
  {
    path: '',
    // pathMatch: 'full',
    loadChildren: () =>
      import('./modules/main/main.module').then((m) => m.MainModule),
  },
  {
    path: 'notfound',
    component: PageNotFoundComponent,
  },
  {
    path: '**',
    pathMatch: 'full',
    redirectTo: '/',
  },
];
