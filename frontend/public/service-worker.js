// REMZA019 Gaming - Service Worker for PWA
// Version 1.5.0 - FIXED CACHE ERRORS

const CACHE_NAME = 'remza019-gaming-v4';  // Updated version to force cache refresh
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json'
];

// Install event - cache resources with individual error handling
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(async (cache) => {
        console.log('[Service Worker] Caching app shell');
        // Cache each URL individually to avoid total failure
        const cachePromises = urlsToCache.map(async (url) => {
          try {
            await cache.add(url);
            console.log(`[Service Worker] Cached: ${url}`);
          } catch (err) {
            console.warn(`[Service Worker] Failed to cache ${url}:`, err.message);
          }
        });
        await Promise.all(cachePromises);
        console.log('[Service Worker] Cache initialization complete');
      })
      .catch((err) => {
        console.error('[Service Worker] Cache open failed:', err);
      })
  );
  self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  return self.clients.claim();
});

// Fetch event - Improved handling for different request types
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests (POST, PUT, DELETE, etc) - CRITICAL FIX
  if (event.request.method !== 'GET') {
    event.respondWith(fetch(event.request));
    return;
  }
  
  // Skip chrome-extension and other unsupported schemes
  const url = event.request.url;
  if (url.startsWith('chrome-extension') || 
      url.startsWith('moz-extension') || 
      url.startsWith('safari-extension') ||
      url.startsWith('edge-extension')) {
    event.respondWith(fetch(event.request));
    return;
  }
  
  // NETWORK FIRST for API calls (never cache API responses)
  if (url.includes('/api/')) {
    event.respondWith(
      fetch(event.request)
        .catch(() => {
          // Only fallback to cache if offline and it exists
          return caches.match(event.request);
        })
    );
    return;
  }
  
  // CACHE FIRST for static assets only (images, fonts, CSS, JS)
  if (url.match(/\.(jpg|jpeg|png|gif|svg|woff|woff2|ttf|css|js)$/)) {
    event.respondWith(
      caches.match(event.request)
        .then((response) => {
          if (response) {
            return response;
          }
          
          return fetch(event.request).then((response) => {
            // Only cache successful responses
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            
            const responseToCache = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache).catch(() => {
                // Silently fail if caching fails
              });
            });
            
            return response;
          });
        })
    );
    return;
  }
  
  // For everything else, just fetch without caching
  event.respondWith(fetch(event.request));
});

// Listen for messages from clients
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

console.log('[Service Worker] Loaded successfully');
