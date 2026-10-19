const MAPPINGS: Array<[string, string, string]> = [
  ['Embeddings', 'Deterministic hashing (256-d)', 'Managed embeddings / Vertex / Azure OpenAI'],
  ['Vector index', 'In-memory cosine', 'OpenSearch / Azure AI Search / Vertex Vector Search'],
  ['Keyword', 'Local BM25 + RRF', 'Same hybrid pattern in managed search'],
  ['ACL', 'YAML principals + metadata filter', 'IdP claims + document ACLs / row-level security'],
  ['Grounding', 'Extractive sentences + cite gate', 'Hosted LLM with citation / abstain policy'],
  ['Eval', 'Offline YAML fixtures + pytest', 'Online RAGAS / custom faithfulness judges'],
]

export function EngineeringPage() {
  return (
    <div className="page">
      <div className="label" style={{ color: 'var(--cyan)' }}>
        Engineering · simulated vs production
      </div>
      <h1 className="page-title">
        Honest local stack. <em>Documented</em> cloud analogues.
      </h1>
      <p className="lede">
        This portfolio demo proves control flow — retrieve, authorize, ground, abstain — without a
        billable cloud surface. Production swaps are mappings, not pretence that cloud is running.
      </p>

      <div className="tablewrap">
        <table className="stack">
          <thead>
            <tr>
              <th>Capability</th>
              <th>Local (this demo)</th>
              <th>Production analogue</th>
            </tr>
          </thead>
          <tbody>
            {MAPPINGS.map(([cap, local, prod]) => (
              <tr key={cap}>
                <td>{cap}</td>
                <td>{local}</td>
                <td>{prod}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="sec-head">
        <span className="label">Design principles</span>
        <h2>Fail closed, cite everything, ACL after retrieve</h2>
      </div>
      <div className="grid3">
        <div className="card">
          <h3>Fail closed</h3>
          <p>Unknown classifications deny. Thin evidence refuses. Never invent policy text.</p>
        </div>
        <div className="card">
          <h3>Citations mandatory</h3>
          <p>Answered claims must map to authorized excerpts with doc_id + section.</p>
        </div>
        <div className="card">
          <h3>ACL after retrieve</h3>
          <p>Denials are explicit and testable — Bob cannot cite POL-HR-001.</p>
        </div>
      </div>
    </div>
  )
}
