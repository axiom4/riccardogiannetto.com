export {};

declare global {
  interface Window {
    __zone_symbol__PASSIVE_EVENTS: string[];
  }
}

window.__zone_symbol__PASSIVE_EVENTS = ['touchstart', 'wheel'];
