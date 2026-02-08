import { Component, OnInit, inject, signal, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
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
export class PostDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private blogService = inject(BlogService);
  
  post = signal<Post | null>(null);
  parsedBody = signal('');
  loading = signal(true);
  error = signal<string | null>(null);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      // Chiama l'API per ottenere il dettaglio del post
      this.blogService.blogPostsRetrieve({ id: +id }).subscribe({
        next: async (post: Post) => {
          this.post.set(post);
          if (post.body) {
            const parsed = await marked.parse(post.body);
            this.parsedBody.set(parsed);
          }
          this.loading.set(false);
        },
        error: (err: unknown) => {
          console.error('Error loading post:', err);
          this.error.set(
            'Impossibile caricare il post. Potrebbe non esistere o esserci un problema di rete.'
          );
          this.loading.set(false);
        },
      });
    } else {
      this.error.set('ID del post non valido.');
      this.loading.set(false);
    }
  }

  getFeaturedImageUrl(post: Post): string {
    return post.image ? `/api/blog/posts/${post.id}/width/1200` : '';
  }
}
