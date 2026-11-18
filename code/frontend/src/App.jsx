import { useEffect, useState } from 'react'

import { getHealth } from './api/health.js'

export default function App() {
  // null while the answer has not arrived yet.
  const [apiStatus, setApiStatus] = useState(null)

  useEffect(() => {
    getHealth()
      .then(() => setApiStatus('ok'))
      .catch(() => setApiStatus('not reachable'))
  }, [])

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-2">
      <h1 className="text-3xl font-semibold">ClassCraft</h1>
      <p className="text-slate-600">
        {apiStatus === null ? 'API: checking…' : `API: ${apiStatus}`}
      </p>
    </main>
  )
}
