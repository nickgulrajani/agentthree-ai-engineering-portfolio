export type Health = {
  ok: boolean
  version: string
  project: string
  chunkCount: number
  zeroCost: boolean
  billableSurface: boolean
  embeddings: string
  grounding: string
  message: string
}

export type Principal = {
  principalId: string
  displayName: string
  department: string
  clearance: string
  roles: string[]
}

export type CorpusDoc = {
  docId: string
  title: string
  classification: string
  allowedDepartments: string[]
  allowedRoles: string[]
  source: string
  chunkCount: number
}

export type Citation = {
  docId: string
  title: string
  section: string
  chunkId: string
  classification: string
  source: string
  excerpt: string
}

export type AskResult = {
  principal: Principal
  question: string
  answered: boolean
  answer: string
  refusalReason: string | null
  evidenceCount: number
  topScore: number
  citations: Citation[]
}

export type EvalCase = {
  caseId: string
  passed: boolean
  checks: Record<string, boolean>
  detail: string
}

export type Evaluation = {
  score: number
  passed: number
  failed: number
  total: number
  ok: boolean
  zeroCost: boolean
  results: EvalCase[]
}

export type Preset = {
  id: string
  label: string
  principalId: string
  question: string
  expect: string
}
