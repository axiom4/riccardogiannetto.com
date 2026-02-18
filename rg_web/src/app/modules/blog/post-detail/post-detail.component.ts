import {
  Component,
  inject,
  signal,
  ChangeDetectionStrategy,
} from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { Meta, Title } from '@angular/platform-browser';
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
  private meta = inject(Meta);
  private titleService = inject(Title);
  private location = inject(Location);

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

        // Update SEO
        this.titleService.setTitle(post.title + ' | Riccardo Giannetto Blog');
        this.meta.updateTag({ name: 'description', content: post.summary || post.title });
        
        // Open Graph
        this.meta.updateTag({ property: 'og:title', content: post.title });
        this.meta.updateTag({ property: 'og:description', content: post.summary || post.title });
        this.meta.updateTag({ property: 'og:type', content: 'article' });
        
        if (post.image) {
            // Assuming image path/URL structure. Adjust as needed.
            // Using window.location.origin is browser-only, but Angular Universal usually handles this if configured.
            // Safe fallback if not SSR:
            const origin = typeof window !== 'undefined' ? window.location.origin : '';
            this.meta.updateTag({ property: 'og:image', content: `${origin}/api/blog/posts/${post.id}/width/1200` });
        }
        
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
