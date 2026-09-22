// Offline-First Service Worker for Smiling Critters 3D Sky & Airplane Adventure (Bay Area -> Boston)

const CACHE_NAME = 'critters-airplane-3d-v1';
const PRECACHE_URLS = [
  './',
  './index.html',
  './manifest.json',
  './assets/custom_critter_fox_lantern.jpg',
  './assets/custom_critter_bat_moonstar.jpg',
  './src/vendor/three.min.js',
  './src/vendor/OrbitControls.js',
  './src/styles/main.css',
  './src/audio/soundSynth.js',
  './src/characters/materials.js',
  './src/characters/SunnyFox.js',
  './src/characters/LunaBat.js',
  './src/characters/animations.js',
  './src/characters/particles.js',
  './src/aircraft/aircraftFactory.js',
  './src/aircraft/contrailSystem.js',
  './src/flight/skyCourse.js',
  './src/main.js',
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS).catch(() => {}))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) return caches.delete(key);
          return null;
        })
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request)
        .then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => caches.match('./index.html'));
    })
  );
});
