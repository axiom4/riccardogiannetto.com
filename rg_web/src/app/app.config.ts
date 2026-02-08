import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter, withInMemoryScrolling } from '@angular/router';

import { routes } from './app.routes';
import { Configuration, ConfigurationParameters } from './modules/core/api/v1';
import { environment } from '../environments/environment';
import { provideHttpClient, withFetch } from '@angular/common/http';
import { IMAGE_LOADER } from '@angular/common';
import { galleryLoaderProvider } from './image-loader.config';

export function apiConfigFactory(): Configuration {
  const params: ConfigurationParameters = {
    basePath: environment.api_url,
  };
  return new Configuration(params);
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
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
      provide: IMAGE_LOADER,
      useValue: galleryLoaderProvider,
    },
  ],
};
