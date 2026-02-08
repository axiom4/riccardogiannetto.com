import { ImageLoaderConfig } from '@angular/common';

export const galleryLoaderProvider = (config: ImageLoaderConfig) => {
  // If width is provided, use it.
  if (config.width) {
    return `${config.src}/width/${config.width}`;
  }
  // If no width is provided (e.g. for the fallback src), default to a reasonable large width like 1920
  // to ensures we hit the image binary endpoint and not the JSON details endpoint.
  return `${config.src}/width/1920`;
};
