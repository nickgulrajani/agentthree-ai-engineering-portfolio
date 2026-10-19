import type { AskResult, CorpusDoc, Evaluation, Health, Principal } from './types'

const API = ''

async function getJson<T>(path: string): Promise<T> {
  const r = await fetch(`${API}${path}`)
  if (!r.ok) throw new Error(`${path} → ${r.status}`)
  return r.json() as Promise<T>
}

export function fetchHealth(): Promise<Health> {
  return getJson('/api/health')
}

export async function fetchPrincipals(): Promise<Principal[]> {
  const body = await getJson<{ principals: Principal[] }>('/api/principals')
  return body.principals
}

export async function fetchCorpus(): Promise<{ documents: CorpusDoc[]; chunkCount: number }> {
  return getJson('/api/corpus')
}

export async function askQuestion(principalId: string, question: string): Promise<AskResult> {
  const r = await fetch(`${API}/api/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ principal_id: principalId, question }),
  })
  if (!r.ok) {
    const detail = await r.text()
    throw new Error(detail || `ask → ${r.status}`)
  }
  return r.json() as Promise<AskResult>
}

export function fetchEvaluation(): Promise<Evaluation> {
  return getJson('/api/evaluation')
}
