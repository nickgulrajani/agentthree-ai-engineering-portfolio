export function ArchitectureDiagram() {
  return (
    <div className="diagram" aria-label="Enterprise RAG architecture">
      <svg viewBox="0 0 1100 220" role="img">
        <defs>
          <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#8fa6cf" />
          </marker>
        </defs>

        {[
          { x: 20, label: 'Markdown\npolicies', sub: 'ACL metadata' },
          { x: 230, label: 'Ingest /\nchunk', sub: 'local' },
          { x: 440, label: 'Hybrid\nretrieve', sub: 'vector + BM25 + RRF' },
          { x: 650, label: 'ACL\nfilter', sub: 'clearance · dept · roles' },
          { x: 860, label: 'Ground or\nrefuse', sub: 'citations · fail closed' },
        ].map((n) => (
          <g key={n.x}>
            <rect
              x={n.x}
              y={48}
              width={160}
              height={100}
              rx={12}
              fill="#151a25"
              stroke="#33405c"
              strokeWidth={1.5}
            />
            {n.label.split('\n').map((line, i) => (
              <text
                key={line}
                x={n.x + 80}
                y={88 + i * 20}
                textAnchor="middle"
                fill="#f2f6ff"
                fontFamily="Syne, sans-serif"
                fontSize={16}
                fontWeight={700}
              >
                {line}
              </text>
            ))}
            <text
              x={n.x + 80}
              y={132}
              textAnchor="middle"
              fill="#8fa6cf"
              fontFamily="DM Mono, monospace"
              fontSize={11}
            >
              {n.sub}
            </text>
          </g>
        ))}

        {[180, 390, 600, 810].map((x) => (
          <line
            key={x}
            x1={x}
            y1={98}
            x2={x + 48}
            y2={98}
            stroke="#8fa6cf"
            strokeWidth={2}
            markerEnd="url(#arrow)"
          />
        ))}

        <text x={730} y={30} fill="#22d3ee" fontFamily="DM Mono, monospace" fontSize={12}>
          Principal identity
        </text>
        <line x1={730} y1={36} x2={730} y2={48} stroke="#22d3ee" strokeWidth={1.5} strokeDasharray="4 3" />
      </svg>
    </div>
  )
}
