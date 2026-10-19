import { useEffect, useState } from 'react'
import { fetchEvaluation } from '../api'
import type { EvaluationResponse, EvalRow } from '../types'

function pct(n: number) {
  return `${Math.round(n * 100)}%`
}

function CaseRows({ rows }: { rows: EvalRow[] }) {
  return (
    <div className="tablewrap" style={{ marginTop: 18 }}>
      <table className="stack">
        <thead>
          <tr>
            <th>Case</th>
            <th>Expected</th>
            <th>Actual</th>
            <th>Result</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>
                <div>{r.label || r.id}</div>
                <div className="meta mono">{r.id}</div>
              </td>
              <td>
                <span className="mono">{r.expected}</span>
              </td>
              <td>
                <span className="mono">{r.actual}</span>
              </td>
              <td>
                <span className={`pill ${r.pass ? 'p-met' : 'p-not'}`}>{r.pass ? 'Pass' : 'Fail'}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function EvaluationPage() {
  const [data, setData] = useState<EvaluationResponse | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [showPublished, setShowPublished] = useState(false)

  useEffect(() => {
    fetchEvaluation()
      .then((d) => {
        setData(d)
        setErr(null)
      })
      .catch((e) => setErr(e instanceof Error ? e.message : String(e)))
  }, [])

  if (err) {
    return (
      <div className="page">
        <div className="sec-head" style={{ marginTop: 0 }}>
          <span className="label">Evaluation</span>
          <h2>Agent outcome accuracy</h2>
        </div>
        <p className="lede" style={{ color: 'var(--red)' }}>
          Could not load metrics — is the backend running? ({err})
        </p>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="page">
        <div className="sec-head" style={{ marginTop: 0 }}>
          <span className="label">Evaluation</span>
          <h2>Agent outcome accuracy</h2>
        </div>
        <p className="lede">Loading published results…</p>
      </div>
    )
  }

  const view = showPublished && data.latest ? data.published : data.active
  const accuracy = view.outcomeAccuracy

  return (
    <div className="page">
      <div className="sec-head" style={{ marginTop: 0 }}>
        <span className="label">Evaluation</span>
        <h2>How the agents scored on golden cases</h2>
      </div>
      <p className="lede">
        Deterministic offline scorer (`evaluation/run_eval.py`) — CPT 72148 / AHP-RAD-014. No Gemini required.
        {data.using === 'latest'
          ? ' Showing your latest local run; committed baseline is still available.'
          : ' Showing the committed baseline from published_results.json.'}
      </p>

      <div className="eval-metrics">
        <div className="eval-metric">
          <div className="label">Outcome accuracy</div>
          <div className="eval-num" style={{ color: accuracy >= 1 ? 'var(--lime)' : 'var(--amber)' }}>
            {pct(accuracy)}
          </div>
          <div className="meta">
            {view.passed} / {view.cases} cases
          </div>
        </div>
        <div className="eval-metric">
          <div className="label">Golden cases</div>
          <div className="eval-num">{view.cases}</div>
          <div className="meta">meets · pend · urgent</div>
        </div>
        <div className="eval-metric">
          <div className="label">Source</div>
          <div className="eval-source mono">{view.baseline ? 'published baseline' : 'last local run'}</div>
          <div className="meta">{view.source}</div>
        </div>
      </div>

      {data.latest && (
        <div className="row2" style={{ marginTop: 8, marginBottom: 4, alignItems: 'center' }}>
          <button type="button" className="btn ghost" onClick={() => setShowPublished((v) => !v)}>
            {showPublished ? 'Show latest local run' : 'Compare to committed baseline'}
          </button>
        </div>
      )}

      <CaseRows rows={view.rows} />

      <p className="meta" style={{ marginTop: 16 }}>
        Re-score locally: <span className="mono">.venv/bin/python -m evaluation.run_eval</span> — writes{' '}
        <span className="mono">evaluation/last_results.json</span>, then refresh this tab.
      </p>
    </div>
  )
}
