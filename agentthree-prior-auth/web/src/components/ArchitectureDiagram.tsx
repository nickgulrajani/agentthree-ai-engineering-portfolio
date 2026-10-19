/** Architecture SVG from the AgentThree guide (Overview). */
export function ArchitectureDiagram() {
  // Layout constants — keep A2A corridors ≥ label pill width so text never meets box edges.
  const a1 = { x: 168, w: 210 }
  const gap = 168
  const a2 = { x: a1.x + a1.w + gap, w: 210 }
  const a3 = { x: a2.x + a2.w + gap, w: 210 }
  const hitl = { x: a3.x + a3.w + 56, w: 118 }
  const vbW = hitl.x + hitl.w + 16

  const mid12 = a1.x + a1.w + gap / 2
  const mid23 = a2.x + a2.w + gap / 2
  const c1 = a1.x + a1.w / 2
  const c2 = a2.x + a2.w / 2
  const c3 = a3.x + a3.w / 2
  const mcpX = a1.x
  const mcpW = a3.x + a3.w - a1.x

  return (
    <div className="diagram" role="img" aria-label="Architecture: Provider to Intake, Prior Auth, CDS over A2A, MCP tools below, HITL and audit.">
      <svg viewBox={`0 0 ${vbW} 520`} xmlns="http://www.w3.org/2000/svg" fontFamily="DM Sans, sans-serif">
        <defs>
          <marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill="#ff4fd8" />
          </marker>
          <marker id="arc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill="#22d3ee" />
          </marker>
          <marker id="arw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill="#b9cdf0" />
          </marker>
        </defs>

        {/* Provider */}
        <rect x="14" y="70" width="120" height="120" rx="10" fill="#151a25" stroke="#33405c" />
        <text x="74" y="112" textAnchor="middle" fill="#f2f6ff" fontFamily="Syne, sans-serif" fontWeight="700" fontSize="14">
          Provider
        </text>
        <text x="74" y="132" textAnchor="middle" fill="#b9cdf0" fontSize="11.5">
          EHR / portal
        </text>
        <text x="74" y="150" textAnchor="middle" fill="#b9cdf0" fontSize="11.5">
          Da Vinci PAS
        </text>
        <text x="74" y="168" textAnchor="middle" fill="#b9cdf0" fontSize="11.5">
          FHIR bundle
        </text>
        <line x1="136" y1="130" x2={a1.x - 4} y2="130" stroke="#b9cdf0" strokeWidth="1.5" markerEnd="url(#arw)" />

        {/* Agent 1 */}
        <g>
          <rect x={a1.x} y="50" width={a1.w} height="160" rx="12" fill="#0f1117" stroke="#a3e635" strokeWidth="1.5" />
          <rect x={a1.x} y="50" width={a1.w} height="5" rx="2" fill="#a3e635" />
          <text x={a1.x + 16} y="82" fill="#a3e635" fontFamily="DM Mono, monospace" fontSize="10.5" letterSpacing="1.2">
            AGENT 1 · ADK
          </text>
          <text x={a1.x + 16} y="104" fill="#f2f6ff" fontFamily="Syne, sans-serif" fontWeight="700" fontSize="15">
            Clinical Intake
          </text>
          <text x={a1.x + 16} y="128" fill="#b9cdf0" fontSize="12">
            Extract conditions, meds, findings
          </text>
          <text x={a1.x + 16} y="146" fill="#b9cdf0" fontSize="12">
            Normalize to FHIR R4 / RxNorm
          </text>
          <text x={a1.x + 16} y="164" fill="#b9cdf0" fontSize="12">
            Detect documentation gaps
          </text>
          <text x={a1.x + 16} y="190" fill="#8fa6cf" fontFamily="DM Mono, monospace" fontSize="10">
            /.well-known/agent-card.json
          </text>
        </g>

        {/* Agent 2 */}
        <g>
          <rect x={a2.x} y="50" width={a2.w} height="160" rx="12" fill="#0f1117" stroke="#a78bfa" strokeWidth="1.5" />
          <rect x={a2.x} y="50" width={a2.w} height="5" rx="2" fill="#a78bfa" />
          <text x={a2.x + 16} y="82" fill="#a78bfa" fontFamily="DM Mono, monospace" fontSize="10.5" letterSpacing="1.2">
            AGENT 2 · ADK
          </text>
          <text x={a2.x + 16} y="104" fill="#f2f6ff" fontFamily="Syne, sans-serif" fontWeight="700" fontSize="15">
            Prior Authorization
          </text>
          <text x={a2.x + 16} y="128" fill="#b9cdf0" fontSize="12">
            Check eligibility and benefits
          </text>
          <text x={a2.x + 16} y="146" fill="#b9cdf0" fontSize="12">
            Retrieve policy criteria (RAG)
          </text>
          <text x={a2.x + 16} y="164" fill="#b9cdf0" fontSize="12">
            Match criterion by criterion
          </text>
          <text x={a2.x + 16} y="190" fill="#8fa6cf" fontFamily="DM Mono, monospace" fontSize="10">
            /.well-known/agent-card.json
          </text>
        </g>

        {/* Agent 3 — title split so it stays inside the box */}
        <g>
          <rect x={a3.x} y="50" width={a3.w} height="160" rx="12" fill="#0f1117" stroke="#ffb020" strokeWidth="1.5" />
          <rect x={a3.x} y="50" width={a3.w} height="5" rx="2" fill="#ffb020" />
          <text x={a3.x + 16} y="82" fill="#ffb020" fontFamily="DM Mono, monospace" fontSize="10.5" letterSpacing="1.2">
            AGENT 3 · ADK
          </text>
          <text x={a3.x + 16} y="102" fill="#f2f6ff" fontFamily="Syne, sans-serif" fontWeight="700" fontSize="15">
            Clinical Decision
          </text>
          <text x={a3.x + 16} y="120" fill="#f2f6ff" fontFamily="Syne, sans-serif" fontWeight="700" fontSize="15">
            Support
          </text>
          <text x={a3.x + 16} y="142" fill="#b9cdf0" fontSize="12">
            Retrieve guidelines (vector+graph)
          </text>
          <text x={a3.x + 16} y="158" fill="#b9cdf0" fontSize="12">
            Cited, confidence-scored findings
          </text>
          <text x={a3.x + 16} y="174" fill="#b9cdf0" fontSize="12">
            Grounding guardrail
          </text>
          <text x={a3.x + 16} y="196" fill="#8fa6cf" fontFamily="DM Mono, monospace" fontSize="10">
            /.well-known/agent-card.json
          </text>
        </g>

        {/* HITL */}
        <rect x={hitl.x} y="70" width={hitl.w} height="120" rx="10" fill="#151a25" stroke="#22d3ee" strokeWidth="1.5" />
        <text x={hitl.x + hitl.w / 2} y="104" textAnchor="middle" fill="#22d3ee" fontFamily="DM Mono, monospace" fontSize="10" letterSpacing="1">
          HITL GATE
        </text>
        <text x={hitl.x + hitl.w / 2} y="126" textAnchor="middle" fill="#f2f6ff" fontFamily="Syne, sans-serif" fontWeight="700" fontSize="13">
          Human review
        </text>
        <text x={hitl.x + hitl.w / 2} y="148" textAnchor="middle" fill="#b9cdf0" fontSize="10.5">
          Approve · Request info
        </text>
        <text x={hitl.x + hitl.w / 2} y="166" textAnchor="middle" fill="#b9cdf0" fontSize="10.5">
          Escalate to MD
        </text>

        {/* MCP layer */}
        <line x1={c1} y1="212" x2={c1} y2="262" stroke="#22d3ee" strokeWidth="1.5" markerEnd="url(#arc)" />
        <line x1={c2} y1="212" x2={c2} y2="262" stroke="#22d3ee" strokeWidth="1.5" markerEnd="url(#arc)" />
        <line x1={c3} y1="212" x2={c3} y2="262" stroke="#22d3ee" strokeWidth="1.5" markerEnd="url(#arc)" />
        <rect x={mcpX} y="266" width={mcpW} height="54" rx="10" fill="rgba(34,211,238,.08)" stroke="#22d3ee" strokeWidth="1.5" />
        <text x={c2} y="290" textAnchor="middle" fill="#f2f6ff" fontFamily="Syne, sans-serif" fontWeight="700" fontSize="15">
          Model Context Protocol
        </text>
        <text x={c2} y="309" textAnchor="middle" fill="#b9cdf0" fontSize="11.5">
          tools/list · tools/call · streamable HTTP · scoped identity · PHI-minimized responses
        </text>

        {/* Data stores */}
        <g fontSize="11.5">
          {[
            { t: 'FHIR R4', a: 'Patient, Condition', b: 'MedicationStatement' },
            { t: 'Terminology', a: 'RxNorm (RxNav)', b: 'ICD-10-CM, CPT' },
            { t: 'Payer policy', a: 'Coverage criteria', b: 'versioned chunks' },
            { t: 'Eligibility', a: 'Benefits, plan', b: 'claims history' },
            { t: 'Knowledge', a: 'Guidelines', b: 'literature' },
            { t: 'Vector + graph', a: 'FAISS / Weaviate', b: 'Neo4j' },
          ].map((d, i) => {
            const storeW = (mcpW - 5 * 16) / 6
            const x = mcpX + i * (storeW + 16)
            return (
              <g key={d.t} transform={`translate(${x},350)`}>
                <rect width={storeW} height="76" rx="8" fill="#151a25" stroke="#33405c" />
                <text x="10" y="22" fill="#f2f6ff" fontWeight="700">
                  {d.t}
                </text>
                <text x="10" y="42" fill="#b9cdf0">
                  {d.a}
                </text>
                <text x="10" y="58" fill="#b9cdf0">
                  {d.b}
                </text>
              </g>
            )
          })}
        </g>
        <line x1={c2} y1="322" x2={c2} y2="346" stroke="#22d3ee" strokeWidth="1.5" markerEnd="url(#arc)" />

        {/* Audit */}
        <rect x="14" y="452" width={vbW - 28} height="50" rx="10" fill="rgba(163,230,53,.06)" stroke="#a3e635" strokeDasharray="5 4" />
        <text x="32" y="482" fill="#a3e635" fontFamily="DM Mono, monospace" fontSize="12" letterSpacing="1">
          AUDIT + OBSERVABILITY
        </text>
        <text x="210" y="482" fill="#b9cdf0" fontSize="12">
          Every A2A message, MCP call, model call, guardrail, and human decision → OTel span + SHA-256 hash-chained ledger
        </text>

        {/* A2A connectors drawn last so labels always sit above box fills */}
        <A2ALink x1={a1.x + a1.w + 4} x2={a2.x - 4} y={120} mid={mid12} sub="message/send" />
        <A2ALink x1={a2.x + a2.w + 4} x2={a3.x - 4} y={120} mid={mid23} sub="task context" />
        <line x1={a3.x + a3.w + 4} y1="130" x2={hitl.x - 4} y2="130" stroke="#ff4fd8" strokeWidth="2" markerEnd="url(#ar)" />
      </svg>
    </div>
  )
}

/** Label pill centered in the corridor — width capped so it cannot touch agent boxes. */
function A2ALink({ x1, x2, y, mid, sub }: { x1: number; x2: number; y: number; mid: number; sub: string }) {
  const pillW = 118
  const pillH = 34
  return (
    <g>
      <line x1={x1} y1={y} x2={x2} y2={y} stroke="#ff4fd8" strokeWidth="2" markerEnd="url(#ar)" />
      <rect
        x={mid - pillW / 2}
        y={y - pillH - 6}
        width={pillW}
        height={pillH}
        rx="6"
        fill="#0f1117"
        stroke="#ff4fd8"
        strokeWidth="1"
      />
      <text x={mid} y={y - pillH + 8} textAnchor="middle" fill="#ff4fd8" fontFamily="DM Mono, monospace" fontSize="11">
        A2A
      </text>
      <text x={mid} y={y - 10} textAnchor="middle" fill="#ff4fd8" fontFamily="DM Mono, monospace" fontSize="9">
        {sub}
      </text>
    </g>
  )
}
