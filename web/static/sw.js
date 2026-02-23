// TOXIC LYRICALLY — Service Worker
// Cache version — bump this string to force cache refresh on deploy
const CACHE_NAME = 'toxic-v2';

// Assets to pre-cache on install
const PRECACHE_URLS = [
  '/',
  '/tour/',
  '/music/',
  '/static/css/output.css',
  '/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
];

// ── Install: pre-cache core assets ──────────────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_URLS);
    }).then(() => self.skipWaiting())
  );
});

// ── Activate: remove old caches ─────────────────────────────────
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    }).then(() => self.clients.claim())
  );
});

// ── Fetch: strategy per request type ────────────────────────────
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET and cross-origin requests (e.g. YouTube iframes, Google Fonts)
  if (request.method !== 'GET' || url.origin !== location.origin) {
    return;
  }

  // Skip Django admin, HTMX partial requests and media uploads
  if (
    url.pathname.startsWith('/admin/') ||
    url.pathname.startsWith('/media/') ||
    request.headers.get('HX-Request')
  ) {
    return;
  }

  // Static assets: Cache-First (fast, long-lived)
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(request).then((cached) => {
        return cached || fetch(request).then((response) => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          return response;
        });
      })
    );
    return;
  }

  // HTML pages: Network-First (fresh content, offline fallback)
  event.respondWith(
    fetch(request)
      .then((response) => {
        const clone = response.clone();
        // Only cache successful navigation responses
        if (response.ok && response.type === 'basic') {
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
        }
        return response;
      })
      .catch(() => {
        return caches.match(request).then((cached) => {
          return cached || caches.match('/');
        });
      })
  );
});
