// Sends a single background push to a subscription captured from the PWA.
//
// Usage:
//   1. node generate-vapid.js          (writes vapid.json)
//   2. Subscribe in the PWA, copy the subscription JSON into subscription.json
//   3. node send.js                    (sends a silent + haptic push)
//      node send.js --sound            (control: push that may make sound)
//
// This is the real test: the device should be LOCKED / app BACKGROUNDED when
// you run this. Then observe: does it vibrate? Does it stay silent?

import webpush from 'web-push';
import { readFileSync } from 'node:fs';

const vapid = JSON.parse(readFileSync('vapid.json', 'utf8'));
const subscription = JSON.parse(readFileSync('subscription.json', 'utf8'));

// Contact email is required by the VAPID spec; any mailto works for the spike.
webpush.setVapidDetails('mailto:spike@example.com', vapid.publicKey, vapid.privateKey);

const wantSound = process.argv.includes('--sound');

const payload = JSON.stringify({
  title: 'Anchor spike',
  body: wantSound ? 'Control push (sound allowed).' : 'Silent + haptic background push.',
  tag: 'anchor-spike-bg',
  silent: !wantSound,            // the property under test
  vibrate: [200, 100, 200],      // the haptic pattern under test
  requireInteraction: true,
});

try {
  const res = await webpush.sendNotification(subscription, payload, { TTL: 60 });
  console.log('Push sent. HTTP', res.statusCode, '— now check the device.');
  console.log(wantSound ? 'Mode: WITH SOUND (control)' : 'Mode: SILENT + HAPTIC');
} catch (err) {
  console.error('Push failed:', err.statusCode, err.body || err.message);
  if (err.statusCode === 410 || err.statusCode === 404) {
    console.error('Subscription expired/invalid — re-subscribe in the PWA and refresh subscription.json.');
  }
}
