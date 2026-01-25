import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { BlogService, PostPreview } from '../../core/api/v1';

@Component({
  selector: 'app-post-list',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './post-list.component.html',
  styleUrls: ['./post-list.component.scss'],
})
export class PostListComponent implements OnInit {
  private blogService = inject(BlogService);
  posts: PostPreview[] = [];
  isLoading = true;
  error: string | null = null;

  ngOnInit(): void {
    // Chiama l'API per ottenere la lista dei post
    this.blogService.blogPostsList().subscribe({
      next: (response: { results: PostPreview[] }) => {
        this.posts = response.results;
        this.isLoading = false;
      },
      error: (error: unknown) => {
        console.error('Error fetching posts:', error);
        this.error = 'Impossibile caricare i post. Riprova più tardi.';
        this.isLoading = false;
      },
    });
  }

  getThumbnailUrl(url: string | undefined): string {
    return url || '';
  }
}
