// Minimaler Dienst für die Installation: Seite bleibt auch ohne Netz startbar.
const V = 'bh-2';
self.addEventListener('install', e => { self.skipWaiting(); e.waitUntil(caches.open(V).then(c => c.addAll(['./', 'icons/icon-192.png']).catch(() => {}))); });
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== V).map(x => caches.delete(x)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  if (new URL(e.request.url).origin !== self.location.origin) return; // Produktbilder vom Shop nicht zwischenspeichern
  e.respondWith(fetch(e.request).then(r => { const k = r.clone(); caches.open(V).then(c => c.put(e.request, k)); return r; }).catch(() => caches.match(e.request)));
});
