import { useEffect, useState } from 'react'
import './App.css'
import { fetchHealth } from './api'
import { EngineeringPage } from './pages/EngineeringPage'
import { EvaluationPage } from './pages/EvaluationPage'
import { LiveAskPage } from './pages/LiveAskPage'
import { OverviewPage } from './pages/OverviewPage'
import type { Health } from './types'

type View = 'overview' | 'ask' | 'eval' | 'eng'

const NAV: Array<{ id: View; label: string }> = [
  { id: 'overview', label: 'Overview' },
  { id: 'ask', label: 'Live ask' },
  { id: 'eval', label: 'Evaluation' },
  { id: 'eng', label: 'Engineering' },
]

export default function App() {
  const [view, setView] = useState<View>('overview')
  const [health, setHealth] = useState<Health | null>(null)
  const [healthErr, setHealthErr] = useState(false)

  useEffect(() => {
    fetchHealth()
      .then((h) => {
        setHealth(h)
        setHealthErr(false)
      })
      .catch(() => setHealthErr(true))
  }, [])

  return (
    <div className="app">
      <header className="top">
        <div className="brand">
          <span className="dots">
            <i style={{ background: 'var(--lime)' }} />
            <i style={{ background: 'var(--violet)' }} />
            <i style={{ background: 'var(--amber)' }} />
          </span>
          AgentThree
        </div>
        <span className="badge">Enterprise RAG · zero cost</span>
        <nav className="tabs" role="tablist" aria-label="Sections">
          {NAV.map((n) => (
            <button
              key={n.id}
              type="button"
              role="tab"
              aria-selected={view === n.id}
              onClick={() => setView(n.id)}
            >
              {n.label}
            </button>
          ))}
        </nav>
        <span className={`health ${healthErr ? 'bad' : health ? 'ok' : ''}`}>
          {healthErr
            ? 'API offline — run agentthree-rag serve'
            : health
              ? `local · ${health.chunkCount} chunks · $0`
              : 'connecting…'}
        </span>
      </header>

      <main>
        {view === 'overview' && <OverviewPage onGoLive={() => setView('ask')} />}
        {view === 'ask' && <LiveAskPage />}
        {view === 'eval' && <EvaluationPage />}
        {view === 'eng' && <EngineeringPage />}
      </main>
    </div>
  )
}
