import {
  Component,
  inject,
  signal,
  ChangeDetectionStrategy,
} from '@angular/core';
import {
  BlogService,
  Page,
} from '../../../core/api/v1';
import { ActivatedRoute, Router } from '@angular/router';
import { Title } from '@angular/platform-browser';
import { HighlightService } from '../../../main/highlight.service';
import { DatePipe } from '@angular/common';
import { marked } from 'marked';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { catchError, EMPTY, filter, map, switchMap, tap } from 'rxjs';

@Component({
  selector: 'app-page',
  templateUrl: './page.component.html',
  styleUrl: './page.component.scss',
  imports: [DatePipe],
  providers: [HighlightService],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PageComponent {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private blogService = inject(BlogService);
  private title = inject(Title);
  private highlightService = inject(HighlightService);

  page = signal<Page | undefined>(undefined);
  parsedBody = signal<string>('');
  highlighted = signal<boolean>(false);
  tag = signal<string>('');

  constructor() {
    this.route.paramMap
      .pipe(
        takeUntilDestroyed(),
        map((params) => params.get('tag')),
        filter((tag): tag is string => !!tag),
        tap((tag) => {
          this.tag.set(tag);
          this.page.set(undefined);
          this.parsedBody.set('');
          this.highlighted.set(false);
        }),
        switchMap((tag) =>
          this.blogService.blogPagesRetrieve({ tag: tag }).pipe(
            catchError((error) => {
              console.log(error);
              this.router.navigate(['/notfound']);
              return EMPTY;
            })
          )
        )
      )
      .subscribe(async (page) => {
        this.page.set(page);
        this.title.setTitle(page.title);

        if (page.body) {
          try {
            const parsed = await marked.parse(page.body);
            this.parsedBody.set(parsed);
          } catch (e) {
            console.error('Markdown parsing error', e);
          }
        }

        // Timeout to allow DOM update before highlighting
        setTimeout(() => {
          this.highlightService.highlightAll();
          this.highlighted.set(true);
        });
      });
  }
}
