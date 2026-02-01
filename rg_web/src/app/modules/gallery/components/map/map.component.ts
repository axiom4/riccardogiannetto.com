import {
  Component,
  PLATFORM_ID,
  OnDestroy,
  ViewEncapsulation,
  ViewChild,
  ElementRef,
  inject,
  AfterViewInit,
} from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { PortfolioService } from '../../../core/api/v1';

// Import Leaflet types ensuring no runtime import (SSR safe)
import * as LeafletTypes from 'leaflet';

interface ImageLocation {
  id: number;
  title: string;
  latitude?: number | null;
  longitude?: number | null;
  thumbnail: string;
}

@Component({
  selector: 'app-gallery-map',
  templateUrl: './map.component.html',
  styleUrls: ['./map.component.scss'],
  standalone: true,
  encapsulation: ViewEncapsulation.None,
})
export class MapComponent implements OnDestroy, AfterViewInit {
  @ViewChild('map') mapContainer!: ElementRef;
  private map: LeafletTypes.Map | undefined;

  private platformId = inject(PLATFORM_ID);
  private portfolioService = inject(PortfolioService);

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
    import('leaflet').then((module) => {
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
        this.map?.invalidateSize();
      }, 100);

      // Fetch Locations and add markers
      this.fetchLocations(L);
    });
  }

  private fetchLocations(L: typeof LeafletTypes): void {
    this.portfolioService.portfolioImagesLocationsList().subscribe({
      next: (response: ImageLocation[]) => {
        const locations = response as ImageLocation[];

        // Use featureGroup as basic cluster fallback if markerCluster is missing
        const leafletWithCluster = L as typeof LeafletTypes & {
          markerClusterGroup?: () => LeafletTypes.FeatureGroup;
        };

        const markers = leafletWithCluster.markerClusterGroup
          ? leafletWithCluster.markerClusterGroup()
          : L.featureGroup();

        locations.forEach((loc) => {
          if (loc.latitude == null || loc.longitude == null) return;

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

        this.map?.addLayer(markers);

        // Fit bounds if we have markers
        if (locations.length > 0) {
          const bounds = markers.getBounds();
          if (bounds.isValid()) {
            this.map?.fitBounds(bounds, { padding: [50, 50] });
          }
        }
      },
      error: (err) => {
        console.error('Failed to load photo locations', err);
      },
    });
  }
}
