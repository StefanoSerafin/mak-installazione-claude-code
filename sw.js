// Service worker: la guida resta consultabile anche senza rete dopo la prima apertura.
// Prima la rete (così si vede sempre l'ultima versione), copia salvata se la rete manca o tarda oltre 3,5 secondi.
const CACHE = 'mak-installazione-claude-code-v1';
const FILE = ['./', 'index.html'];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(FILE); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (nomi) {
    return Promise.all(nomi.filter(function (n) { return n !== CACHE; }).map(function (n) { return caches.delete(n); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener('fetch', function (e) {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (url.origin !== self.location.origin) return;
  if (/\.(zip|pdf)$/i.test(url.pathname)) return; // download: sempre dalla rete
  const salvata = function () { return caches.match(e.request, { ignoreSearch: true }); };
  e.respondWith(new Promise(function (risolvi) {
    let fatto = false;
    const attesa = setTimeout(function () {
      salvata().then(function (r) { if (r && !fatto) { fatto = true; risolvi(r); } });
    }, 3500);
    fetch(e.request).then(function (r) {
      clearTimeout(attesa);
      if (r.ok) { const copia = r.clone(); caches.open(CACHE).then(function (c) { c.put(e.request, copia); }); }
      if (!fatto) { fatto = true; risolvi(r); }
    }).catch(function () {
      clearTimeout(attesa);
      salvata().then(function (r) { if (!fatto) { fatto = true; risolvi(r || Response.error()); } });
    });
  }));
});
