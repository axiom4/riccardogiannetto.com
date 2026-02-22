import { ApplicationConfig, provideZonelessChangeDetection } from '@angular/core';
import { provideRouter, withInMemoryScrolling } from '@angular/router';

import { routes } from './app.routes';
import { Configuration, ConfigurationParameters } from './modules/core/api/v1';
import { environment } from '../environments/environment';
import { provideHttpClient, withFetch } from '@angular/common/http';
import { IMAGE_CONFIG, IMAGE_LOADER } from '@angular/common';
import { galleryLoaderProvider } from './image-loader.config';

export function apiConfigFactory(): Configuration {
  const params: ConfigurationParameters = {
    basePath: environment.api_url,
  };
  return new Configuration(params);
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideZonelessChangeDetection(),
    provideRouter(
      routes,
      withInMemoryScrolling({
        anchorScrolling: 'disabled',
        scrollPositionRestoration: 'top',
      }),
    ),
    { provide: Configuration, useFactory: apiConfigFactory },
    provideHttpClient(withFetch()),
    {
      provide: IMAGE_CONFIG,
      useValue: {
        breakpoints: [
          320, 480, 640, 750, 828, 960, 1080, 1200, 1920, 2048, 3840,
        ],
      },
    },
    {
      provide: IMAGE_LOADER,
      useValue: galleryLoaderProvider,
    },
  ],
};
