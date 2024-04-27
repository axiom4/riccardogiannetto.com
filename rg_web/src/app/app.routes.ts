import { Routes } from '@angular/router';
import { MainPageComponent } from './main-page/main-page.component';
import { PageNotFoundComponent } from './page-not-found/page-not-found.component';

export const routes: Routes = [
  {
    path: 'pages',
    loadChildren: () => import('./modules/page/page.module').then(m => m.PageModule)
  },
  {
    path: 'blog',
    loadChildren: () => import('./modules/blog/blog.module').then(m => m.BlogModule)
  },
  {
    path: '',
    pathMatch: 'full',
    component: MainPageComponent
  },
  {
    path: 'notfound',
    component: PageNotFoundComponent
  },
  {
    path: '**',
    pathMatch: 'full',
    redirectTo: "/notfound"
  }
];
