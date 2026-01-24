import { Injectable, PLATFORM_ID, inject } from '@angular/core';

import { isPlatformBrowser } from '@angular/common';

@Injectable()
export class HighlightService {
  private platformId = inject<Object>(PLATFORM_ID);


  async highlightAll() {
    if (isPlatformBrowser(this.platformId)) {
      const Prism = (await import('prismjs')).default;

      await Promise.all([
        import('prismjs/plugins/toolbar/prism-toolbar'),
        import('prismjs/plugins/copy-to-clipboard/prism-copy-to-clipboard'),
        import('prismjs/components/prism-css'),
        import('prismjs/components/prism-javascript'),
        import('prismjs/components/prism-java'),
        import('prismjs/components/prism-bash'),
        import('prismjs/components/prism-yaml'),
        import('prismjs/components/prism-markup'),
        import('prismjs/components/prism-typescript'),
        import('prismjs/components/prism-sass'),
        import('prismjs/components/prism-scss'),
        import('prismjs/components/prism-vim'),
      ]);

      Prism.highlightAll();
    }
  }
}
