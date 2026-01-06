const CACHE_NAME = 'esp8266-dash-v1';
const ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/icon-512.png',
    'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap',
    'https://cdn.jsdelivr.net/npm/chart.js'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(ASSETS))
    );
});

self.addEventListener('fetch', (event) => {
    // For API requests, try network first, falling back to nothing (or custom offline JSON)
    if (event.request.url.includes('/api/') || event.request.url.includes('/relay/')) {
        event.respondWith(
            fetch(event.request).catch(() => {
                // Return a clear error or fallback json if offline
                return new Response(JSON.stringify({ error: 'offline' }), {
                    headers: { 'Content-Type': 'application/json' }
                });
            })
        );
        return;
    }

    // For other requests (HTML, CSS, JS), try cache first, then network
    event.respondWith(
        caches.match(event.request)
            .then((response) => response || fetch(event.request))
    );
});
