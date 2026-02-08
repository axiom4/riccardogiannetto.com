import {
  Component,
  inject,
  signal,
  ChangeDetectionStrategy,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { catchError, EMPTY, filter, map, switchMap, tap } from 'rxjs';
import { BlogService, Post } from '../../core/api/v1';
import { marked } from 'marked';

@Component({
  selector: 'app-post-detail',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './post-detail.component.html',
  styleUrls: ['./post-detail.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PostDetailComponent {
  private route = inject(ActivatedRoute);
  private blogService = inject(BlogService);

  post = signal<Post | null>(null);
  parsedBody = signal('');
  loading = signal(true);
  error = signal<string | null>(null);

  constructor() {
    this.route.paramMap
      .pipe(
        takeUntilDestroyed(),
        map((params) => params.get('id')),
        filter((id): id is string => !!id),
        tap(() => {
          this.loading.set(true);
          this.error.set(null);
          this.post.set(null);
          this.parsedBody.set('');
        }),
        switchMap((id) =>
          this.blogService.blogPostsRetrieve({ id: +id }).pipe(
            catchError((err: unknown) => {
              console.error('Error loading post:', err);
              this.error.set(
                'Impossibile caricare il post. Potrebbe non esistere o esserci un problema di rete.',
              );
              this.loading.set(false);
              return EMPTY;
            }),
          ),
        ),
      )
      .subscribe(async (post: Post) => {
        this.post.set(post);
        if (post.body) {
          try {
            const parsed = await marked.parse(post.body);
            this.parsedBody.set(parsed);
          } catch (e) {
            console.error('Error parsing markdown:', e);
          }
        }
        this.loading.set(false);
      });
  }

  getFeaturedImageUrl(post: Post): string {
    return post.image ? `/api/blog/posts/${post.id}/width/1200` : '';
  }
}
