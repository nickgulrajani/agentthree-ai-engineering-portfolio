import { useEffect, useState } from 'react'
import { fetchEvaluation } from '../api'
import type { Evaluation } from '../types'

export function EvaluationPage() {
  const [evalData, setEvalData] = useState<Evaluation | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function load() {
    setBusy(true)
    setError(null)
    try {
      setEvalData(await fetchEvaluation())
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Eval failed')
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  return (
    <div className="page">
      <div className="label" style={{ color: 'var(--cyan)' }}>
        Offline evaluation · YAML fixtures
      </div>
      <h1 className="page-title">
        Faithfulness, citations, <em>ACL</em>
      </h1>
      <p className="lede">
        Fixture cases exercise authorized answer, ACL deny, public access, fabrication refusal, and
        eng on-call — no LLM judge, no cloud score.
      </p>

      <div className="ctrl" style={{ marginBottom: 16 }}>
        <button type="button" className="btn primary" disabled={busy} onClick={() => void load()}>
          {busy ? 'Running…' : 'Re-run evaluation'}
        </button>
      </div>

      {error && <p className="err">{error}</p>}

      {evalData && (
        <>
          <div className="eval-metrics">
            <div className="eval-metric">
              <span className="label">Score</span>
              <div className="eval-num" style={{ color: evalData.ok ? 'var(--lime)' : 'var(--red)' }}>
                {(evalData.score * 100).toFixed(0)}%
              </div>
            </div>
            <div className="eval-metric">
              <span className="label">Passed</span>
              <div className="eval-num">
                {evalData.passed}/{evalData.total}
              </div>
            </div>
            <div className="eval-metric">
              <span className="label">Cost</span>
              <div className="eval-source">{evalData.zeroCost ? 'Local · $0' : '—'}</div>
            </div>
          </div>

          <div className="tablewrap">
            <table className="stack">
              <thead>
                <tr>
                  <th>Case</th>
                  <th>Pass</th>
                  <th>Checks</th>
                  <th>Detail</th>
                </tr>
              </thead>
              <tbody>
                {evalData.results.map((r) => (
                  <tr key={r.caseId}>
                    <td className="mono">{r.caseId}</td>
                    <td style={{ color: r.passed ? 'var(--lime)' : 'var(--red)' }}>
                      {r.passed ? 'PASS' : 'FAIL'}
                    </td>
                    <td>
                      {Object.entries(r.checks)
                        .map(([k, v]) => `${k}=${v ? '✓' : '✗'}`)
                        .join(', ')}
                    </td>
                    <td>{r.detail}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
