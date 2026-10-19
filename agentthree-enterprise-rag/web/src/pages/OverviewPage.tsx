import { useEffect, useState } from 'react'
import { ArchitectureDiagram } from '../components/ArchitectureDiagram'
import { fetchCorpus } from '../api'
import type { CorpusDoc } from '../types'

const PIPELINE: Array<[string, string]> = [
  ['Ingest', 'Markdown policies with YAML ACL frontmatter'],
  ['Embed', 'Deterministic hashing vectors — no model download'],
  ['Retrieve', 'Hybrid vector + BM25 fused with RRF'],
  ['Authorize', 'Clearance · department · roles (fail closed)'],
  ['Ground', 'Extractive sentences + mandatory citations'],
  ['Abstain', 'Refuse when evidence is thin or unauthorized'],
]

export function OverviewPage({ onGoLive }: { onGoLive: () => void }) {
  const [docs, setDocs] = useState<CorpusDoc[]>([])
  const [chunks, setChunks] = useState(0)

  useEffect(() => {
    fetchCorpus()
      .then((c) => {
        setDocs(c.documents)
        setChunks(c.chunkCount)
      })
      .catch(() => {
        setDocs([])
        setChunks(0)
      })
  }, [])

  return (
    <div className="page">
      <div className="hero-grid">
        <div>
          <div className="label" style={{ color: 'var(--cyan)' }}>
            Enterprise knowledge · Hybrid RAG + metadata ACL
          </div>
          <h1 className="page-title">
            Answers only from <em>authorized</em> documents.
          </h1>
          <p className="lede">
            Ask as Alice, Bob, or Eve. The agent retrieves with hybrid search, filters by clearance,
            returns grounded citations — or refuses when evidence is missing. Entirely local; zero
            billable surface.
          </p>
          <button type="button" className="btn primary" onClick={onGoLive}>
            Open Live ask →
          </button>
        </div>
        <div className="banner">
          <b>How to demo.</b> Start here for the architecture story, then switch to <b>Live ask</b>{' '}
          and run the four presets: authorized answer → ACL deny → public ok → fabrication refuse.
        </div>
      </div>

      <div className="sec-head">
        <span className="label">01 · What this proves</span>
        <h2>Not a chatbot — authorized retrieval with abstention</h2>
      </div>
      <div className="grid3">
        <div className="card">
          <h3>Same question, different access</h3>
          <p>
            Alice (HR, confidential) sees the $75 stipend. Bob (Engineering, internal) is refused —
            the confidential HR policy never enters his context.
          </p>
        </div>
        <div className="card">
          <h3>Citations or silence</h3>
          <p>
            Every answered claim cites <code>doc_id</code> + section + excerpt. No evidence in corpus
            ⇒ refuse, never invent policy.
          </p>
        </div>
        <div className="card">
          <h3>Zero billable surface</h3>
          <p>
            Hashing embeddings, in-memory BM25, extractive grounding. No OpenAI, Anthropic, Pinecone,
            or cloud vector DB.
          </p>
        </div>
      </div>

      <div className="sec-head">
        <span className="label">02 · Architecture</span>
        <h2>Ingest → hybrid retrieve → ACL → ground or refuse</h2>
      </div>
      <ArchitectureDiagram />

      <div className="sec-head">
        <span className="label">03 · Local pipeline</span>
        <h2>How the free stack maps to enterprise search</h2>
      </div>
      <div className="tablewrap">
        <table className="stack">
          <thead>
            <tr>
              <th>Stage</th>
              <th>Local implementation</th>
            </tr>
          </thead>
          <tbody>
            {PIPELINE.map(([stage, detail]) => (
              <tr key={stage}>
                <td>{stage}</td>
                <td>{detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="sec-head">
        <span className="label">04 · Demo corpus</span>
        <h2>
          {docs.length || '—'} policies · {chunks || '—'} chunks
        </h2>
      </div>
      <div className="tablewrap">
        <table className="stack">
          <thead>
            <tr>
              <th>Doc</th>
              <th>Title</th>
              <th>Class</th>
              <th>Depts</th>
              <th>Chunks</th>
            </tr>
          </thead>
          <tbody>
            {docs.map((d) => (
              <tr key={d.docId}>
                <td className="mono">{d.docId}</td>
                <td>{d.title}</td>
                <td>{d.classification}</td>
                <td>{d.allowedDepartments.join(', ') || '—'}</td>
                <td>{d.chunkCount}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
