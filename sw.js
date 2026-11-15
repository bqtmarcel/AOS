/* AOS Service Worker – speichert nur die App-Dateien für den Offline-Start.
   Trainingsdaten laufen nicht über den Service Worker (Anfragen an api.github.com werden nicht zwischengespeichert). */
const CACHE = 'aos-74089112742c';
const FILES = ['./', './index.html', './manifest.webmanifest', './apple-touch-icon.png', './icon-192.png', './icon-512.png', './icon-maskable-512.png', './img/tiger.png?v=1', './img/t.png?v=1'];

self.addEventListener('install', e => {
  // cache:'reload' umgeht den Browser-Cache, damit wirklich die neue Version gespeichert wird
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES.map(f => new Request(f, { cache: 'reload' })))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith('aos-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;
  if (req.mode === 'navigate') {
    // Online: immer die aktuelle Seite (max. 4 s warten), offline: gespeicherte Version
    e.respondWith((async () => {
      try {
        const net = await Promise.race([fetch(req, { cache: 'no-store' }), new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), 4000))]);
        if (net && net.ok) { const c = await caches.open(CACHE); c.put('./index.html', net.clone()); return net; }
        throw new Error('bad');
      } catch (err) { return (await caches.match('./index.html')) || fetch(req); }
    })());
    return;
  }
  e.respondWith(caches.match(req).then(r => r || fetch(req)));
});
