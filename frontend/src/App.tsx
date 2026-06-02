import { useEffect, useState } from 'react'

type Health =
  | { state: 'loading' }
  | { state: 'ok'; status: string; service: string }
  | { state: 'error'; message: string }

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8080'

export default function App() {
  const [health, setHealth] = useState<Health>({ state: 'loading' })

  useEffect(() => {
    let cancelled = false
    fetch(`${API_URL}/healthz`)
      .then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => {
        if (!cancelled) setHealth({ state: 'ok', status: data.status, service: data.service })
      })
      .catch((err) => {
        if (!cancelled) setHealth({ state: 'error', message: String(err.message ?? err) })
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <main className="min-h-full flex flex-col items-center justify-center px-6 text-center">
      <h1 className="text-3xl font-semibold tracking-tight">Anchor</h1>
      <p className="mt-2 text-neutral-400">The app loaded.</p>

      <div className="mt-10 w-full max-w-sm rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6">
        <p className="text-xs uppercase tracking-wide text-neutral-500">Backend</p>

        {health.state === 'loading' && (
          <p className="mt-3 text-lg text-neutral-300">Checking…</p>
        )}

        {health.state === 'ok' && (
          <div className="mt-3">
            <p className="text-lg text-emerald-400">Connected</p>
            <p className="mt-1 text-neutral-400">
              {health.service} · {health.status}
            </p>
          </div>
        )}

        {health.state === 'error' && (
          <div className="mt-3">
            <p className="text-lg text-amber-400">Not reachable</p>
            <p className="mt-1 break-words text-sm text-neutral-500">{health.message}</p>
          </div>
        )}

        <p className="mt-5 break-all text-xs text-neutral-600">{API_URL}/healthz</p>
      </div>
    </main>
  )
}
