// REMZA019 Gaming - Service Worker for PWA
// Version 1.5.0 - CHROME EXTENSION FIX & THEME SWITCHER

const CACHE_NAME = 'remza019-gaming-v1.5.0-chrome-extension-fixed';
const urlsToCache = [
  '/',
  '/index.html',
  '/static/css/main.css',
  '/static/js/main.js',
  '/remza-logo.png',
  '/logo192.png',
  '/logo512.png',
  '/favicon.png',
  '/manifest.json'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Caching app shell');
        return cache.addAll(urlsToCache);
      })
      .catch((err) => {
        console.log('[Service Worker] Cache failed:', err);
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

// Fetch event - NETWORK FIRST for JS/CSS, cache for images
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // ⚠️ CRITICAL FIX: Ignore non-HTTP(S) requests (chrome-extension://, data:, blob:, etc.)
  // This prevents "Request scheme 'chrome-extension' is unsupported" errors
  if (!event.request.url.startsWith('http')) {
    console.log(`[Service Worker] Ignoring non-HTTP request: ${event.request.url.substring(0, 50)}...`);
    return; // Let browser handle it naturally
  }
  
  // NETWORK FIRST for JavaScript and CSS to get latest code
  if (url.pathname.match(/\.(js|css)$/)) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Clone and cache
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          }).catch((err) => {
            console.log('[Service Worker] Cache put failed:', err);
          });
          return response;
        })
        .catch(() => {
          // Fallback to cache if offline
          return caches.match(event.request);
        })
    );
    return;
  }
  
  // CACHE FIRST for everything else (images, etc)
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        if (response) {
          return response;
        }
        
        const fetchRequest = event.request.clone();
        
        return fetch(fetchRequest).then((response) => {
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          
          const responseToCache = response.clone();
          
          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(event.request, responseToCache);
            })
            .catch((err) => {
              console.log('[Service Worker] Cache put failed:', err);
            });
          
          return response;
        });
      })
  );
});

// Listen for messages from clients
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

console.log('[Service Worker] Loaded successfully');
