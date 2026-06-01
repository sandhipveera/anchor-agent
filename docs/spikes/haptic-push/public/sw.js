/*
 * Service worker for the Anchor haptic-push spike.
 *
 * Purpose: prove (or disprove) that we can deliver a BACKGROUND push that
 *   (a) makes NO sound, and
 *   (b) produces a haptic vibration,
 * reliably, on a real Android device with the PWA installed and not foregrounded.
 *
 * Key Android/Chrome facts this exercises:
 *  - Web Push on Android Chrome requires `userVisibleOnly: true`, so every push
 *    MUST show a notification. There is no truly invisible background push.
 *    The question is therefore: can the *shown* notification be soundless +
 *    haptic? This SW sets `silent` and `vibrate` to test exactly that.
 *  - Background vibration comes from the SYSTEM notification (the `vibrate`
 *    option below), NOT from navigator.vibrate() (which only runs in a
 *    foregrounded page). The OS notification channel can still override this.
 */

self.addEventListener('install', (event) => {
  // Activate immediately so testing doesn't require a reload dance.
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('push', (event) => {
  let payload = {};
  try {
    payload = event.data ? event.data.json() : {};
  } catch (e) {
    payload = { title: 'Anchor spike', body: event.data ? event.data.text() : '(no data)' };
  }

  const title = payload.title || 'Anchor spike';
  const options = {
    body: payload.body || 'Background push received.',
    tag: payload.tag || 'anchor-spike',
    // The two properties under test:
    silent: payload.silent !== false,            // default: silent (no sound)
    vibrate: payload.vibrate || [200, 100, 200], // haptic pattern
    // Keep it on screen until acknowledged so the tester can confirm it fired.
    requireInteraction: payload.requireInteraction !== false,
    // Avoid renotify sound/behavior surprises.
    renotify: false,
    data: { receivedAtClientNote: 'see report; do not log real user content in prod' },
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clients) => {
      for (const client of clients) {
        if ('focus' in client) return client.focus();
      }
      if (self.clients.openWindow) return self.clients.openWindow('./index.html');
    })
  );
});
