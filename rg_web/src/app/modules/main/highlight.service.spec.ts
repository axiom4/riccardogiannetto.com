import { provideZonelessChangeDetection } from '@angular/core';
import { TestBed } from '@angular/core/testing';

import { HighlightService } from './highlight.service';

describe('HighlightService', () => {
  let service: HighlightService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideZonelessChangeDetection()],
    });
    service = TestBed.inject(HighlightService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
