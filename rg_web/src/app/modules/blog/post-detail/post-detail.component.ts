import { Component, OnInit, inject } from '@angular/core';
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
})
export class PostDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private blogService = inject(BlogService);
  post: Post | null = null;
  parsedBody = '';

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      // Chiama l'API per ottenere il dettaglio del post
      this.blogService.blogPostsRetrieve({ id: +id }).subscribe({
        next: async (post: Post) => {
          this.post = post;
          if (this.post.body) {
            this.parsedBody = await marked.parse(this.post.body);
          }
        },
        error: (err: unknown) => console.error('Error loading post:', err),
      });
    }
  }

  getFeaturedImageUrl(url: string | undefined): string {
    return url ? `${url}/width/1200` : '';
  }
}
