// Generates a VAPID keypair for the spike.
// Run once:  node generate-vapid.js
// Paste the PUBLIC key into the PWA's "VAPID public key" field.
// Keep the PRIVATE key local; pass it to send.js via env or vapid.json.

import webpush from 'web-push';
import { writeFileSync } from 'node:fs';

const keys = webpush.generateVAPIDKeys();
writeFileSync('vapid.json', JSON.stringify(keys, null, 2));

console.log('VAPID keypair written to vapid.json\n');
console.log('PUBLIC  (paste into the PWA):');
console.log('  ' + keys.publicKey + '\n');
console.log('PRIVATE (stays here, used by send.js):');
console.log('  ' + keys.privateKey + '\n');
