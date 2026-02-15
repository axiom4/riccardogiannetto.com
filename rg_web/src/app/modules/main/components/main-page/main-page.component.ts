import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { GalleryLightboxComponent } from '../../../gallery/components/gallery-lightbox/gallery-lightbox.component';
import { ActivatedRoute } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';

@Component({
  selector: 'app-main-page',
  standalone: true,
  imports: [GalleryLightboxComponent],
  templateUrl: './main-page.component.html',
  styleUrl: './main-page.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MainPageComponent {
  private route = inject(ActivatedRoute);

  id = toSignal(
    this.route.paramMap.pipe(map((params) => params.get('id') ?? undefined))
  );
}
