/* AOS Service Worker – speichert nur die App-Dateien für den Offline-Start.
   Trainingsdaten laufen nicht über den Service Worker (Anfragen an api.github.com werden nicht zwischengespeichert). */
const CACHE = 'aos-02cb4588072a';
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

/* Erinnerungen: Push-Nachrichten aus der GitHub Action im Datenrepo anzeigen.
   Inhalt: { title, body, tag, url } – url ist relativ zur App (z. B. "#training"). */
self.addEventListener('push', e => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch (err) { d = { body: e.data ? e.data.text() : '' }; }
  e.waitUntil(self.registration.showNotification(d.title || 'AOS', {
    body: d.body || '',
    tag: d.tag || 'aos',
    icon: './icon-192.png',
    badge: './icon-192.png',
    data: { url: d.url || '' }
  }));
});
self.addEventListener('notificationclick', e => {
  e.notification.close();
  const target = new URL(self.registration.scope + ((e.notification.data && e.notification.data.url) || '')).href;
  e.waitUntil((async () => {
    const list = await clients.matchAll({ type: 'window', includeUncontrolled: true });
    for (const c of list) {
      if (c.url.startsWith(self.registration.scope)) { await c.focus(); if ('navigate' in c) { try { await c.navigate(target); } catch (err) {} } return; }
    }
    if (clients.openWindow) await clients.openWindow(target);
  })());
});
