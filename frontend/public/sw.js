/*
 * Minimal service worker — present so Chrome treats the app as installable on
 * Android. Intentionally tiny for the Phase-0 shell: it claims clients and
 * passes fetches through to the network. Real caching / offline strategy and
 * the haptic push handler (see docs/spikes/haptic-push) come later.
 */

self.addEventListener('install', () => {
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim())
})

self.addEventListener('fetch', (event) => {
  // Network pass-through. A fetch handler is required for installability.
  event.respondWith(fetch(event.request))
})
