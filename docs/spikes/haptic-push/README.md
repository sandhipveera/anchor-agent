# Spike: Silent + Haptic Web Push on Android PWA

**Status:** awaiting results on a real Android device.
**Why this exists:** "Silent by default, haptic-first" (DESIGN_PRINCIPLES §4, §5)
is load-bearing. If a background push can't be reliably soundless *and* haptic on
an Android PWA, the product changes shape. We validate this **before** building
capabilities — see [ARCHITECTURE.md §8](../../../ARCHITECTURE.md#8-the-load-bearing-unknown-silent--haptic-web-push-on-android-pwa).

## The question, precisely

Android Chrome requires `userVisibleOnly: true` for push — so **every push must
show a notification** (there is no invisible background push). The real question
is therefore:

> Can the *shown* notification be **soundless** and **vibrate**, reliably, when
> the device is locked / app backgrounded — and how much of that is controllable
> by us vs. dictated by the OS notification channel?

Secondary: does foreground `navigator.vibrate()` work (it's a separate code path
from the background notification vibration)?

## What's here

```
public/            # the PWA test harness (static)
  index.html       # step-by-step test buttons + live log
  sw.js            # service worker: push handler sets silent + vibrate
  manifest.json    # installable PWA
  icon-192.png     # (add any 192px png — see note below)
  icon-512.png     # (add any 512px png)
server/            # minimal VAPID push sender (Node)
  generate-vapid.js
  send.js
  package.json
```

> **Icons:** `manifest.json` references `icon-192.png` / `icon-512.png`. Drop any
> two solid-color PNGs of those sizes into `public/` so the install prompt
> appears. They don't matter for the test.

## Prerequisites

- An **Android phone** (the actual target device, ideally the user's model) with
  **Chrome**.
- Node.js on your laptop.
- A way to serve `public/` over **HTTPS to the phone** (push + service workers
  require a secure context; `http://<lan-ip>` will **not** work). Pick one:
  - **cloudflared** (fastest, no account): `cloudflared tunnel --url http://localhost:8080`
  - **ngrok**: `ngrok http 8080`
  - **Firebase Hosting** (matches the prod stack): `firebase deploy`

## Run it

```bash
# 1) Generate VAPID keys (laptop, in server/)
cd server && npm install && node generate-vapid.js
#    -> copy the PUBLIC key printed out

# 2) Serve the PWA over HTTPS (separate terminal, in public/)
cd ../public && python3 -m http.server 8080
#    in another terminal: cloudflared tunnel --url http://localhost:8080
#    -> open the https URL on the PHONE in Chrome

# On the PHONE, in the page:
#   - Step 0: confirm secureContext=true
#   - Step 1: tap "Vibrate now" (foreground vibration check)
#   - Step 2: register SW, grant notification permission
#   - Step 3: tap "Show SILENT + vibrate" and "WITH sound (control)"
#   - Install to home screen (Chrome menu -> Add to Home screen)
#   - Step 4: paste the VAPID PUBLIC key, Subscribe, Copy subscription JSON
#   - Send the JSON to your laptop -> save as server/subscription.json

# 3) THE REAL TEST — lock the phone or background the app, then:
cd ../server
node send.js            # silent + haptic
node send.js --sound    # control (sound allowed)
```

## What to observe (fill in the report below)

For each test, note: **did it vibrate?**, **did it make sound?**, **app
foreground / backgrounded / locked?**, and whether toggling the **OS notification
channel** settings (Chrome site notifications) changed the result.

---

## Report

> Fill this in after running on the device. This drives the go/no-go on PWA vs.
> TWA, and whether haptics are foreground-only.

**Device / OS / Chrome version:**
**Date tested:**

| # | Test | Vibrated? | Sound? | App state | Notes |
|---|------|-----------|--------|-----------|-------|
| 1 | Foreground `navigator.vibrate()` | | n/a | foreground | |
| 2 | Local SILENT+vibrate (step 3) | | | foreground | |
| 3 | Local SILENT+vibrate (step 3) | | | backgrounded | |
| 4 | Background push, silent (`send.js`) | | | locked | |
| 5 | Background push, control (`--sound`) | | | locked | |
| 6 | Repeat #4 after 10+ min idle | | | locked | reliability check |

**Did the OS notification channel override `silent`/`vibrate`?**

**Could the user reach a soundless+haptic state without per-notification fiddling?**

### Verdict

- [ ] **PWA viable** — silent + haptic works reliably in background. Proceed with PWA.
- [ ] **Foreground-only haptics** — design interaction patterns around it (fallback a).
- [ ] **Needs TWA** — wrap as Trusted Web Activity for native channel control (fallback b).

### Recommendation to the engineer

_(one paragraph: what we learned, which fallback if any, and the impact on the
build sequence.)_
