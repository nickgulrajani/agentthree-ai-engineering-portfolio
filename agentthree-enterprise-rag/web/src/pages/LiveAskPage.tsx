import { useEffect, useState } from 'react'
import { askQuestion, fetchPrincipals } from '../api'
import { PRESETS } from '../presets'
import type { AskResult, Principal } from '../types'

export function LiveAskPage() {
  const [principals, setPrincipals] = useState<Principal[]>([])
  const [principalId, setPrincipalId] = useState('alice_hr')
  const [question, setQuestion] = useState(PRESETS[0].question)
  const [activePreset, setActivePreset] = useState(PRESETS[0].id)
  const [result, setResult] = useState<AskResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchPrincipals()
      .then((rows) => {
        setPrincipals(rows)
        if (rows.length) {
          setPrincipalId((cur) =>
            rows.some((p) => p.principalId === cur) ? cur : rows[0].principalId,
          )
        }
      })
      .catch(() => setPrincipals([]))
  }, [])

  const selected = principals.find((p) => p.principalId === principalId)

  async function runAsk(nextPrincipal = principalId, nextQuestion = question) {
    setBusy(true)
    setError(null)
    try {
      const res = await askQuestion(nextPrincipal, nextQuestion)
      setResult(res)
    } catch (e) {
      setResult(null)
      setError(e instanceof Error ? e.message : 'Ask failed')
    } finally {
      setBusy(false)
    }
  }

  function applyPreset(id: string) {
    const p = PRESETS.find((x) => x.id === id)
    if (!p) return
    setActivePreset(id)
    setPrincipalId(p.principalId)
    setQuestion(p.question)
    void runAsk(p.principalId, p.question)
  }

  return (
    <div className="page">
      <div className="label" style={{ color: 'var(--cyan)' }}>
        Live ask · switch principal, same corpus
      </div>
      <h1 className="page-title">
        Watch ACL + citations <em>in the answer</em>
      </h1>
      <p className="lede">
        Run the four presets in order. Scenario 1 and 2 use the same question — only clearance
        changes.
      </p>

      <div className="presets" role="group" aria-label="Demo presets">
        {PRESETS.map((p) => (
          <button
            key={p.id}
            type="button"
            className={activePreset === p.id ? 'on' : ''}
            onClick={() => applyPreset(p.id)}
            disabled={busy}
            title={p.expect}
          >
            {p.label}
          </button>
        ))}
      </div>

      <div className="console">
        <div className="pane">
          <div className="pane-h">
            <h3>Ask as principal</h3>
          </div>
          <div className="pane-b">
            <div className="field">
              <span className="label">Principal</span>
              <select
                value={principalId}
                onChange={(e) => {
                  setPrincipalId(e.target.value)
                  setActivePreset('')
                }}
              >
                {(principals.length
                  ? principals
                  : [{ principalId, displayName: principalId, department: '', clearance: '', roles: [] }]
                ).map((p) => (
                  <option key={p.principalId} value={p.principalId}>
                    {p.displayName} ({p.clearance || '…'})
                  </option>
                ))}
              </select>
            </div>
            {selected && (
              <p className="meta-line">
                <span className="mono">{selected.department}</span> · clearance{' '}
                <b>{selected.clearance}</b> · roles {selected.roles.join(', ') || '—'}
              </p>
            )}
            <div className="field">
              <span className="label">Question</span>
              <textarea
                value={question}
                onChange={(e) => {
                  setQuestion(e.target.value)
                  setActivePreset('')
                }}
                rows={5}
              />
            </div>
            <div className="ctrl">
              <button
                type="button"
                className="btn primary"
                disabled={busy || !question.trim()}
                onClick={() => void runAsk()}
              >
                {busy ? 'Retrieving…' : 'Ask'}
              </button>
            </div>
          </div>
        </div>

        <div className="pane">
          <div className="pane-h">
            <h3>{result?.answered ? 'Grounded answer' : result ? 'Refusal' : 'Result'}</h3>
            {result && (
              <span className={`pill ${result.answered ? 'ok' : 'warn'}`}>
                {result.answered ? 'ANSWERED' : 'REFUSED'}
              </span>
            )}
          </div>
          <div className="pane-b">
            {error && <p className="err">{error}</p>}
            {!result && !error && (
              <p className="lede" style={{ margin: 0 }}>
                Pick a preset or ask a policy question. Answers come only from authorized chunks.
              </p>
            )}
            {result && (
              <>
                <pre className="answer-block">{result.answer}</pre>
                {!result.answered && result.refusalReason && (
                  <p className="meta-line">
                    refusal_reason=<span className="mono">{result.refusalReason}</span>
                  </p>
                )}
                <p className="meta-line">
                  evidence={result.evidenceCount} · top_score={result.topScore.toFixed(4)}
                </p>
                {result.citations.length > 0 && (
                  <div className="tablewrap" style={{ marginTop: 12 }}>
                    <table className="stack">
                      <thead>
                        <tr>
                          <th>Doc</th>
                          <th>Section</th>
                          <th>Class</th>
                          <th>Excerpt</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.citations.map((c) => (
                          <tr key={c.chunkId}>
                            <td className="mono">{c.docId}</td>
                            <td>{c.section || '—'}</td>
                            <td>{c.classification}</td>
                            <td>{c.excerpt}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
