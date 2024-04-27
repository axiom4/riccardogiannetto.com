import { AfterViewChecked, Component, OnDestroy, OnInit } from '@angular/core';
import { BlogService, Page, RetrievePageRequestParams } from '../../../core/api/v1';
import { Subscription } from 'rxjs';
import { ActivatedRoute, NavigationEnd, Event, Router } from '@angular/router';
import { Title } from '@angular/platform-browser';
import { HighlightService } from '../../../../highlight.service';
import { MarkedPipe } from "../../../../marked.pipe";
import { DatePipe, NgIf } from '@angular/common';

@Component({
    selector: 'app-page',
    standalone: true,
    templateUrl: './page.component.html',
    styleUrl: './page.component.scss',
    imports: [
      NgIf,
      DatePipe,
      MarkedPipe
    ]
})
export class PageComponent implements OnInit, OnDestroy,AfterViewChecked {
  page: Page | undefined;
  currentRoute: string | undefined;
  subscription: Subscription | undefined;
  highlighted: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private blogService: BlogService,
    private title: Title,
    private highlightService: HighlightService
  ) { }


    ngAfterViewChecked() {
      if (this.page && !this.highlighted) {
        this.highlightService.highlightAll();
        this.highlighted = true;
      }
    }

  ngOnDestroy(): void {
    if (this.subscription)
      this.subscription.unsubscribe();
  }

  ngOnInit(): void {
    const tag = this.route.snapshot.paramMap.get('tag');
    if (tag) {
      this.getPage(tag)
    }

    this.subscription = this.router.events.subscribe((event: Event) => {
      if (event instanceof NavigationEnd) {
        const tag = this.route.snapshot.paramMap.get('tag');
        if (tag) {
          this.page = undefined
          this.getPage(tag)
        }
      }
    });
  }

  getPage(tag: string) {
    const params: RetrievePageRequestParams = {
      tag: tag
    }
    this.blogService.retrievePage(params).subscribe({
      next: (page) => {
        this.page = page
        this.title.setTitle(page.title)
      },
      error: (error) => {
        this.router.navigate(['/notfound'])
        console.log(error)
      }
    })
  }
}
