import {
  Component,
  OnInit,
  PLATFORM_ID,
  OnDestroy,
  ViewEncapsulation,
  ViewChild,
  ElementRef,
  AfterViewInit,
  inject,
} from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { PortfolioService } from '../../../core/api/v1';

interface ImageLocation {
  id: number;
  title: string;
  latitude: number;
  longitude: number;
  thumbnail: string;
}

@Component({
  selector: 'app-gallery-map',
  templateUrl: './map.component.html',
  styleUrls: ['./map.component.scss'],
  standalone: true,
  encapsulation: ViewEncapsulation.None,
})
export class MapComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('map') mapContainer!: ElementRef;
  private map: any; // Leaflet map

  private platformId = inject(PLATFORM_ID);
  private portfolioService = inject(PortfolioService);

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      // We use ngAfterViewInit pattern technically, but dynamic import helps delay.
      // However, to be safe, we should load map after view init.
      // Since import is async, it might likely happen after view init, but let's be safe.
    }
  }

  ngAfterViewInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.loadMap();
    }
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
    }
  }

  private loadMap(): void {
    // Dynamic import of Leaflet to support SSR (if used) and avoid build issues
    import('leaflet').then((module: typeof import('leaflet')) => {
      const L = module.default || module;
      if (!this.mapContainer) return;

      // Fix for default marker icons
      const DefaultIcon = L.icon({
        iconUrl: '/assets/leaflet/marker-icon.png',
        iconRetinaUrl: '/assets/leaflet/marker-icon-2x.png',
        shadowUrl: '/assets/leaflet/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
      });
      L.Marker.prototype.options.icon = DefaultIcon;

      // Initialize Map
      this.map = L.map(this.mapContainer.nativeElement).setView([0, 0], 2);

      // Add Tile Layer
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(this.map);

      // Force a resize check to ensuring tiles render correctly
      setTimeout(() => {
        this.map.invalidateSize();
      }, 100);

      // Fetch Locations and add markers
      this.fetchLocations(L);
    });
  }

  private fetchLocations(L: typeof import('leaflet')): void {
    this.portfolioService.portfolioImagesLocationsRetrieve().subscribe({
      next: (response: ImageLocation[]) => {
        const locations = response;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const markers = (L as any).markerClusterGroup
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          ? (L as any).markerClusterGroup()
          : L.featureGroup();

        locations.forEach((loc) => {
          const popupContent = `
            <div class="popup-content">
                <img src="${loc.thumbnail}" alt="${loc.title}" loading="lazy" />
                <div class="info">
                    <h3>${loc.title}</h3>
                </div>
            </div>
            `;

          const marker = L.marker([loc.latitude, loc.longitude]).bindPopup(
            popupContent,
          );

          markers.addLayer(marker);
        });

        this.map.addLayer(markers);

        // Fit bounds if we have markers
        if (locations.length > 0) {
          this.map.fitBounds(markers.getBounds(), { padding: [50, 50] });
        }
      },
      error: (err) => {
        console.error('Failed to load photo locations', err);
      },
    });
  }
}
