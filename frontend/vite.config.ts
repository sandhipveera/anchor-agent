import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// host: true so the dev/preview server is reachable over the LAN / a tunnel
// (needed to install + test the PWA on a real Android device).
export default defineConfig({
  plugins: [react()],
  server: { host: true, port: 5173 },
  preview: { host: true, port: 4173 },
})
