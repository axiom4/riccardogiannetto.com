import { Routes } from '@angular/router';

export const PAGE_ROUTES: Routes = [
  { path: '', pathMatch: 'full', redirectTo: '/404' },
  {
    path: ':tag',
    loadComponent: () =>
      import('./components/page/page.component').then((m) => m.PageComponent),
  },
];
