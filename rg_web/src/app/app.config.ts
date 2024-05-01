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
  HTTP_INTERCEPTORS,
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

export function apiConfigFactory(): Configuration {
  const params: ConfigurationParameters = {
    basePath: environment.api_url,
  };
  return new Configuration(params);
}

export const authInterceptorProvider: Provider = {
  provide: HTTP_INTERCEPTORS,
  useClass: AuthInterceptor,
  multi: true,
};

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
    authInterceptorProvider,
  ],
};
