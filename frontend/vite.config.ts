import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// host: true so the dev/preview server is reachable over the LAN / a tunnel
// (needed to install + test the PWA on a real Android device).
// allowedHosts lets a cloudflared/ngrok tunnel reach the dev/preview server for
// on-device PWA testing. Scoped to tunnel domains (not a blanket allow); affects
// only the local dev/preview server, never the built app or Cloud Run.
const tunnelHosts = ['.trycloudflare.com', '.ngrok-free.app', '.ngrok.app']

export default defineConfig({
  plugins: [react()],
  server: { host: true, port: 5173, allowedHosts: tunnelHosts },
  preview: { host: true, port: 4173, allowedHosts: tunnelHosts },
})
