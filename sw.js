const CACHE_NAME = 'perspektive-v1';

// Installiert den Service Worker sofort
self.addEventListener('install', (event) => {
  self.skipWaiting();
});

// Übernimmt sofort die Kontrolle über die Seite
self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

// Network-First-Strategie: Lädt immer die frischeste Ausgabe aus dem Netz,
// fällt aber bei Offline-Betrieb (z. B. im Zug) auf den Cache zurück.
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        const responseClone = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseClone);
        });
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
