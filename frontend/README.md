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

## Deployment (Vercel)

Hosted on Vercel (permanent, laptop-independent), pointed at the Cloud Run
backend:

- **Production URL:** https://anchor-agent-iota.vercel.app
- Project `anchor-agent` (scope `sandhipveeras-projects`), framework preset Vite.
- `VITE_API_URL` is set as a Vercel project env var (Production/Preview/Development)
  → the Cloud Run backend. It is **not** read from a local `.env` in CI.
- `vercel.json` sets the Vite preset and a no-cache header on `sw.js` so PWA
  updates propagate.

```bash
cd frontend
vercel --prod --yes        # redeploy production (CLI is already linked via .vercel/)
```

> The bare `anchor-agent.vercel.app` is taken by another account, and the
> scope-suffixed domain is gated by Vercel Authentication — use the `-iota`
> production domain, which is public and stable across deploys.

## Install on Android (verify on the spike device)

Open **https://anchor-agent-iota.vercel.app** in Chrome on the phone, confirm the
backend card shows *Connected*, then **menu → Add to Home screen**. For testing a
local build before deploying, serve `dist/` over a tunnel instead:

```bash
npm run build && npm run preview        # serves dist/ on :4173, host exposed
cloudflared tunnel --url http://localhost:4173   # in another terminal
```

Installability checklist (all satisfied here): served over HTTPS, web app
manifest with 192/512 icons + `display: standalone`, and a registered service
worker with a `fetch` handler (`public/sw.js`).

## What it does

A single screen that confirms the app loaded and calls the backend `/healthz`,
showing connected / not-reachable. `VITE_API_URL` selects the backend.
