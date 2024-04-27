import { ApplicationConfig, importProvidersFrom } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { provideClientHydration } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { ApiModule, Configuration, ConfigurationParameters } from './modules/core/api/v1';
import { HighlightService } from './highlight.service';

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
    importProvidersFrom(HttpClientModule),
    importProvidersFrom(ApiModule.forRoot(apiConfigFactory)),
    HighlightService
  ]
};
