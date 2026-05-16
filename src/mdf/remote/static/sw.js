// Bump version string to bust cache on deploy
const CACHE = 'mdf-2026-v1';

const PRECACHE = [
    '/static/fonts/bebas-neue.woff2',
    '/static/fonts/bebas-neue-latext.woff2',
    '/static/fonts/barlow-400.woff2',
    '/static/fonts/barlow-400-latext.woff2',
    '/static/fonts/barlow-400-viet.woff2',
    '/static/fonts/barlow-500.woff2',
    '/static/fonts/barlow-500-latext.woff2',
    '/static/fonts/barlow-500-viet.woff2',
    '/static/fonts/barlow-600.woff2',
    '/static/fonts/barlow-600-latext.woff2',
    '/static/fonts/barlow-600-viet.woff2',
    '/static/fonts/barlow-700.woff2',
    '/static/fonts/barlow-700-latext.woff2',
    '/static/fonts/barlow-700-viet.woff2',
    '/static/fonts/barlow-condensed-400.woff2',
    '/static/fonts/barlow-condensed-400-latext.woff2',
    '/static/fonts/barlow-condensed-400-viet.woff2',
    '/static/fonts/barlow-condensed-600.woff2',
    '/static/fonts/barlow-condensed-600-latext.woff2',
    '/static/fonts/barlow-condensed-600-viet.woff2',
    '/static/fonts/barlow-condensed-700.woff2',
    '/static/fonts/barlow-condensed-700-latext.woff2',
    '/static/fonts/barlow-condensed-700-viet.woff2',
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE).then(cache => cache.addAll(PRECACHE))
    );
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
        )
    );
    self.clients.claim();
});

self.addEventListener('fetch', event => {
    const { request } = event;
    if (request.method !== 'GET') return;

    const url = new URL(request.url);

    // Static assets: cache-first (fonts, icons, etc.)
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(request).then(cached => {
                if (cached) return cached;
                return fetch(request).then(response => {
                    caches.open(CACHE).then(cache => cache.put(request, response.clone()));
                    return response;
                });
            })
        );
        return;
    }

    // Same-origin pages: network-first, fall back to cache
    if (url.origin === self.location.origin) {
        event.respondWith(
            fetch(request)
                .then(response => {
                    caches.open(CACHE).then(cache => cache.put(request, response.clone()));
                    return response;
                })
                .catch(() => caches.match(request))
        );
    }
});
