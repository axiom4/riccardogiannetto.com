import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, appConfig)
  .then(() => {
    document.querySelectorAll('[ng-version]')
      .forEach(el => el.removeAttribute('ng-version'));
  })
  .catch((err) =>
    console.error(err),
  );
