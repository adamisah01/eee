const CACHE_NAME = 'wastewise-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/offline.html',
  '/css/variables.css',
  '/css/reset.css',
  '/css/layout.css',
  '/css/components.css',
  '/css/animations.css',
  '/js/app.js',
  '/js/router.js',
  '/js/state.js',
  '/js/api.js',
  '/js/storage.js',
  '/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      // Best effort caching, ignore failures for individual files
      return Promise.all(
        ASSETS_TO_CACHE.map(url => {
          return cache.add(url).catch(err => console.warn('Failed to cache:', url, err));
        })
      );
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            return caches.delete(cache);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  
  // API requests -> Network first
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() => {
        // Could return cached responses for GET APIs here if we implemented it
        return new Response(JSON.stringify({ error: 'Network error' }), {
          headers: { 'Content-Type': 'application/json' }
        });
      })
    );
    return;
  }
  
  // Static assets -> Network first, Cache fallback
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Update cache
        if(response.ok) {
           const resClone = response.clone();
           caches.open(CACHE_NAME).then(cache => cache.put(event.request, resClone));
        }
        return response;
      })
      .catch(() => {
        return caches.match(event.request).then((cachedResponse) => {
          return cachedResponse || caches.match('/offline.html');
        });
      })
  );
});
