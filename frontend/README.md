# Anchor frontend

PWA shell — React + TypeScript + Vite + Tailwind. Dark by default, low-motion,
large tap targets (see [DESIGN_PRINCIPLES.md](../DESIGN_PRINCIPLES.md)).

> Final Android delivery is **TWA-wrapped** (per the resolved haptic-push spike,
> ARCHITECTURE.md §8). The PWA shell is the correct Day-1 starting point; TWA
> wrapping is a deployment-time concern, not yet done here.

## Run locally

```bash
cd frontend
npm install
cp .env.example .env        # point VITE_API_URL at your backend
npm run dev                 # http://localhost:5173
```

## Build

```bash
npm run build               # -> dist/
npm run preview             # serve the production build
```

## Install on Android (verify on the spike device)

The PWA needs **HTTPS** to install. Serve `dist/` (or the dev server) over a
tunnel, open it in Chrome on the phone, then **menu → Add to Home screen**:

```bash
npm run build && npm run preview        # serves dist/ on :4173, host exposed
# in another terminal:
cloudflared tunnel --url http://localhost:4173
# open the https URL on the phone, install, launch from the home screen
```

Installability checklist (all satisfied here): served over HTTPS, web app
manifest with 192/512 icons + `display: standalone`, and a registered service
worker with a `fetch` handler (`public/sw.js`).

## What it does

A single screen that confirms the app loaded and calls the backend `/healthz`,
showing connected / not-reachable. `VITE_API_URL` selects the backend.
