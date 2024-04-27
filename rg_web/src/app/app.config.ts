import { ApplicationConfig, importProvidersFrom, isDevMode } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { provideClientHydration } from '@angular/platform-browser';
import { HttpClientModule, provideHttpClient, withFetch } from '@angular/common/http';
import { ApiModule, Configuration, ConfigurationParameters } from './modules/core/api/v1';
import { HighlightService } from './highlight.service';
import { provideServiceWorker } from '@angular/service-worker';

export function apiConfigFactory(): Configuration {
  const params: ConfigurationParameters = {
    // basePath: environment.api_url
    basePath: 'http://localhost:8000'
  }
  return new Configuration(params);
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideClientHydration(),
    importProvidersFrom(ApiModule.forRoot(apiConfigFactory)),
    HighlightService,
    provideHttpClient(withFetch()),
    provideServiceWorker('ngsw-worker.js', {
        enabled: !isDevMode(),
        registrationStrategy: 'registerWhenStable:30000'
    })
]
};
