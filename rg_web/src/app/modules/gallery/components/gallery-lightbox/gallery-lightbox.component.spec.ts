import { provideZonelessChangeDetection } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';

import { GalleryLightboxComponent } from './gallery-lightbox.component';

describe('GalleryLightboxComponent', () => {
  let component: GalleryLightboxComponent;
  let fixture: ComponentFixture<GalleryLightboxComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GalleryLightboxComponent],
      providers: [
        provideZonelessChangeDetection(),
        provideRouter([]),
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(GalleryLightboxComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
