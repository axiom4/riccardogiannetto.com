import {
  ApplicationConfig,
  Provider,
  importProvidersFrom,
  isDevMode,
} from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import {
  provideClientHydration,
  withHttpTransferCacheOptions,
} from '@angular/platform-browser';
import {
  HttpClientModule,
  provideHttpClient,
  withFetch,
} from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import {
  ApiModule,
  Configuration,
  ConfigurationParameters,
} from './modules/core/api/v1';
import { HighlightService } from './highlight.service';
import { provideServiceWorker } from '@angular/service-worker';
import { environment } from '../environments/environment';
import { AuthInterceptor } from './auth.interceptor';
import { CSP_NONCE } from '@angular/core';

export const nonceProvider: Provider[] = [
  {
    provide: CSP_NONCE,
    useValue: '5957472310',
  },
];

export function apiConfigFactory(): Configuration {
  const params: ConfigurationParameters = {
    basePath: environment.api_url,
  };
  return new Configuration(params);
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideClientHydration(
      withHttpTransferCacheOptions({
        includePostRequests: true,
      })
    ),
    provideAnimations(),
    importProvidersFrom(ApiModule.forRoot(apiConfigFactory)),
    HighlightService,
    provideHttpClient(withFetch()),
    importProvidersFrom(HttpClientModule),
    provideServiceWorker('ngsw-worker.js', {
      enabled: !isDevMode(),
      registrationStrategy: 'registerWhenStable:30000',
    }),
    nonceProvider,
  ],
};
