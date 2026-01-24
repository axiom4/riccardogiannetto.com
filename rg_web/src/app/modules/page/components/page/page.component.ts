import { Component, inject, OnInit, signal } from '@angular/core';
import {
  BlogPagesRetrieveRequestParams,
  BlogService,
  Page,
} from '../../../core/api/v1';
import { ActivatedRoute, Router } from '@angular/router';
import { Title } from '@angular/platform-browser';
import { HighlightService } from '../../../main/highlight.service';
import { MarkedPipe } from '../../../main/marked.pipe';
import { AsyncPipe, DatePipe } from '@angular/common';

@Component({
  selector: 'app-page',
  templateUrl: './page.component.html',
  styleUrl: './page.component.scss',
  imports: [DatePipe, MarkedPipe, AsyncPipe],
  providers: [HighlightService],
})
export class PageComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private blogService = inject(BlogService);
  private title = inject(Title);
  private highlightService = inject(HighlightService);

  page = signal<Page | undefined>(undefined);
  highlighted = signal<boolean>(false);
  tag = signal<string>('');

  ngOnInit(): void {
    this.route.paramMap.subscribe((params) => {
      const tag = params.get('tag');
      if (tag) {
        this.tag.set(tag);
        this.page.set(undefined);
        this.highlighted.set(false);
        this.getPage(tag);
      }
    });
  }

  getPage(tag: string) {
    const params: BlogPagesRetrieveRequestParams = {
      tag: tag,
    };
    this.blogService.blogPagesRetrieve(params).subscribe({
      next: (page) => {
        this.page.set(page);
        this.title.setTitle(page.title);
        // Timeout to allow DOM update before highlighting
        setTimeout(() => {
          if (!this.highlighted()) {
            this.highlightService.highlightAll();
            this.highlighted.set(true);
          }
        });
      },
      error: (error) => {
        this.router.navigate(['/notfound']);
        console.log(error);
      },
    });
  }
}
