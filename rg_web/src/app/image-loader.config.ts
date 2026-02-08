import { ImageLoaderConfig } from '@angular/common';

export const galleryLoaderProvider = (config: ImageLoaderConfig) => {
  if (config.width) {
    return `${config.src}/width/${config.width}`;
  }
  return config.src;
};
