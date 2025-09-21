// Service Worker for Progressive Web App
// Version 1.0.0 - Phase 3 Implementation

const CACHE_NAME = 'researchqa-v1.0.0';
const STATIC_CACHE = 'researchqa-static-v1.0.0';
const DYNAMIC_CACHE = 'researchqa-dynamic-v1.0.0';

// Static assets to cache
const STATIC_ASSETS = [
    '/',
    '/static/css/phase3-advanced.css',
    '/static/js/phase3-advanced.js',
    '/static/manifest.json',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://unpkg.com/htmx.org@1.9.10',
    'https://cdn.jsdelivr.net/npm/apexcharts',
    'https://cdn.jsdelivr.net/npm/select2@4.0.13/dist/css/select2.min.css',
    'https://cdn.jsdelivr.net/npm/select2@4.0.13/dist/js/select2.min.js',
    'https://unpkg.com/aos@2.3.4/dist/aos.css',
    'https://unpkg.com/aos@2.3.4/dist/aos.js',
    'https://d3js.org/d3.v7.min.js',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css'
];

// API endpoints to cache
const API_ENDPOINTS = [
    '/api/dashboard/stats',
    '/api/portfolio/summary',
    '/api/research/recent',
    '/api/market/data'
];

// Install event - cache static assets
self.addEventListener('install', event => {
    console.log('SW: Installing...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('SW: Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('SW: Static assets cached');
                return self.skipWaiting();
            })
            .catch(err => {
                console.error('SW: Cache failed', err);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('SW: Activating...');
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('SW: Deleting old cache', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('SW: Claiming clients');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') return;

    // Skip chrome-extension requests
    if (url.protocol === 'chrome-extension:') return;

    // Handle different types of requests
    if (isStaticAsset(request)) {
        event.respondWith(cacheFirst(request));
    } else if (isAPIRequest(request)) {
        event.respondWith(networkFirst(request));
    } else if (isHTMLRequest(request)) {
        event.respondWith(staleWhileRevalidate(request));
    } else {
        event.respondWith(networkFirst(request));
    }
});

// Check if request is for static asset
function isStaticAsset(request) {
    const url = new URL(request.url);
    return url.pathname.match(/\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$/);
}

// Check if request is for API
function isAPIRequest(request) {
    const url = new URL(request.url);
    return url.pathname.startsWith('/api/') || API_ENDPOINTS.some(endpoint => url.pathname.startsWith(endpoint));
}

// Check if request is for HTML
function isHTMLRequest(request) {
    return request.headers.get('accept')?.includes('text/html');
}

// Cache first strategy (for static assets)
async function cacheFirst(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }

        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.error('SW: Cache first failed', error);
        return new Response('Network error', { status: 408 });
    }
}

// Network first strategy (for API requests)
async function networkFirst(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.log('SW: Network failed, trying cache', error);
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        return new Response(JSON.stringify({ error: 'Network unavailable' }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

// Stale while revalidate (for HTML pages)
async function staleWhileRevalidate(request) {
    const cache = await caches.open(DYNAMIC_CACHE);
    const cachedResponse = await cache.match(request);

    const fetchPromise = fetch(request).then(networkResponse => {
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    });

    return cachedResponse || fetchPromise;
}

// Background sync for offline actions
self.addEventListener('sync', event => {
    if (event.tag === 'background-sync') {
        event.waitUntil(handleBackgroundSync());
    }
});

async function handleBackgroundSync() {
    console.log('SW: Handling background sync');
    // Handle any pending offline actions
    try {
        const pendingActions = await getStoredActions();
        for (const action of pendingActions) {
            await executeAction(action);
        }
        await clearStoredActions();
    } catch (error) {
        console.error('SW: Background sync failed', error);
    }
}

// Push notification handler
self.addEventListener('push', event => {
    if (!event.data) return;

    const data = event.data.json();
    const options = {
        body: data.body,
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/icon-72x72.png',
        vibrate: [100, 50, 100],
        data: data.data,
        actions: [
            {
                action: 'view',
                title: 'View',
                icon: '/static/icons/view.png'
            },
            {
                action: 'dismiss',
                title: 'Dismiss',
                icon: '/static/icons/dismiss.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Notification click handler
self.addEventListener('notificationclick', event => {
    event.notification.close();

    if (event.action === 'view' && event.notification.data?.url) {
        event.waitUntil(
            clients.openWindow(event.notification.data.url)
        );
    } else if (event.action === 'dismiss') {
        // Handle dismiss action
        console.log('Notification dismissed');
    }
});

// Helper functions for IndexedDB operations
async function getStoredActions() {
    // Implementation for getting stored offline actions
    return [];
}

async function executeAction(action) {
    // Implementation for executing stored actions
    console.log('Executing action:', action);
}

async function clearStoredActions() {
    // Implementation for clearing stored actions
    console.log('Clearing stored actions');
}

// Share target handler (if supported)
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SHARE_TARGET') {
        event.waitUntil(handleShareTarget(event.data));
    }
});

async function handleShareTarget(data) {
    // Handle shared content
    console.log('Handling share target:', data);
}
