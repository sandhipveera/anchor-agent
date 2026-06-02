# Spike: Silent + Haptic Web Push on Android PWA

**Status:** ✅ resolved (2026-06-01). Verdict: **needs TWA** (fallback b) — a plain
PWA cannot deliver reliable soundless+haptic background push. See the [report](#report) below.
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

Run on a real Android device. This drives the go/no-go on PWA vs. TWA, and
whether haptics are foreground-only.

**Device / OS / Chrome version:** Android 10, Chrome 147 (mobile). Model masked as
"K" by Chrome's reduced UA. Push endpoint: FCM. **`installedStandalone: true`** —
background tests ran as an installed home-screen PWA, so the result is valid for
the real deployment case, not just a browser tab.
**Date tested:** 2026-06-01

| # | Test | Vibrated? | Sound? | App state | Notes |
|---|------|-----------|--------|-----------|-------|
| 1 | Foreground `navigator.vibrate()` | ✅ yes | n/a | foreground | Vibration API works in foreground. |
| 2 | Local SILENT+vibrate (step 3) | ✅ yes | no (silent) | foreground | Foreground SW `showNotification` honored `vibrate`. |
| 3 | Local SILENT+vibrate (step 3) | — | — | backgrounded | Not separately tested; superseded by the real push tests below. |
| 4 | Background push, silent (`send.js`) | ❌ no | ❌ no | locked | **Nothing appeared at all.** `silent:true` suppressed the entire notification, vibration included. |
| 5 | Background push, control (`--sound`) | ❌ no* | ✅ yes | locked | *One vibration on the very first send (before the delivery path settled); never reproduced. After harness fix (unique tag + `urgency:high`): reliable **sound, no vibration** across repeats. |
| 6 | Repeat #5, identical sends | ❌ no | ✅ yes | locked | Reliability check: background haptic never fired again. Sound consistent; vibration absent. |

**Harness confounds found and fixed mid-spike:** (1) all pushes shared one `tag`
with `renotify:false`, so repeats silently *replaced* the prior notification
without re-alerting — masquerading as "no haptic." Fixed with a unique tag per
send. (2) `web-push` defaults to normal priority, which Android **Doze** defers
on a locked device. Fixed with `urgency:'high'`. After both fixes, sound became
reliable and the *absence* of background vibration was confirmed as real, not an
artifact.

**Did the OS notification channel override `silent`/`vibrate`?** Yes. On Android
8+, a web notification's vibration is governed by Chrome's per-site **notification
channel**, not the `vibrate` array we send. We cannot set or guarantee it from
web code. `silent:true` maps to a fully-silent (no-vibrate) behavior; `silent:false`
let sound through but did **not** make the channel vibrate for background pushes.

**Could the user reach a soundless+haptic state without per-notification fiddling?**
Not deterministically, and not from our code. The one configuration that vibrated
also wasn't reproducible, and the reproducible one made sound. There is no
web-controllable path to "reliably soundless **and** reliably haptic" in the
background on this device.

### Verdict

- [ ] **PWA viable** — silent + haptic works reliably in background. Proceed with PWA.
- [ ] **Foreground-only haptics** — design interaction patterns around it (fallback a).
- [x] **Needs TWA** — wrap as Trusted Web Activity for native channel control (fallback b).

### Recommendation to the engineer

A plain Android PWA cannot deliver the product's load-bearing promise — *soundless
by default, haptic-first* — for **background / locked** notifications. Foreground
haptics work (`navigator.vibrate` and foreground `showNotification` both buzz), but
every background path fails the requirement: `silent:true` suppresses the whole
notification (no haptic), and `silent:false` produces sound while the vibration is
left to Chrome's notification channel, which did not fire haptics for background
pushes and is not controllable from web code. Because background haptic reminders
are core (bill reminders, sensory pre-warnings, "where was I" nudges), foreground-only
haptics (fallback a) would gut the product. **Proceed with fallback (b): an
Android TWA** (Trusted Web Activity) with **notification delegation** to an
app-defined notification channel (sound OFF, vibration ON), which gives deterministic
soundless+haptic in the background. Impact on the build sequence: the PWA-vs-TWA gate
in [ARCHITECTURE.md §11](../../../ARCHITECTURE.md#11-build-sequence-current) resolves
to **TWA-wrapped PWA**; the web app, FastAPI backend, and Elastic/ADK work are
otherwise unaffected and can now begin. One artifact-specific note: the TWA wrapper
and its notification channel are the only net-new work this verdict adds; §8 of the
architecture should be updated from "viability under validation" to this resolved
decision.
