import {
  Component,
  inject,
  signal,
  ChangeDetectionStrategy,
  ViewEncapsulation,
} from '@angular/core';
import { CommonModule, NgOptimizedImage } from '@angular/common';
import { RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { BlogService, PostPreview } from '../../core/api/v1';

@Component({
  selector: 'app-post-list',
  standalone: true,
  imports: [CommonModule, RouterLink, NgOptimizedImage],
  templateUrl: './post-list.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None,
})
export class PostListComponent {
  private blogService = inject(BlogService);
  posts = signal<PostPreview[]>([]);
  isLoading = signal(true);
  error = signal<string | null>(null);

  constructor() {
    // Chiama l'API per ottenere la lista dei post
    this.blogService
      .blogPostsList()
      .pipe(takeUntilDestroyed())
      .subscribe({
        next: (response: { results: PostPreview[] }) => {
          this.posts.set(response.results);
          this.isLoading.set(false);
        },
        error: (error: unknown) => {
          console.error('Error fetching posts:', error);
          this.error.set('Impossibile caricare i post. Riprova più tardi.');
          this.isLoading.set(false);
        },
      });
  }
}
