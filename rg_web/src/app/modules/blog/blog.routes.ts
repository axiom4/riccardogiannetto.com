import { Routes } from '@angular/router';
// Assicurati che i percorsi di importazione siano corretti in base a dove hai creato i file
import { PostListComponent } from './post-list/post-list.component';
import { PostDetailComponent } from './post-detail/post-detail.component';

export const BLOG_ROUTES: Routes = [
  {
    path: '',
    component: PostListComponent,
  },
  {
    path: ':id',
    component: PostDetailComponent,
  },
];
