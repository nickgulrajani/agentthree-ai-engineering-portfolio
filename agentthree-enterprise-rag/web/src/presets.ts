import type { Preset } from './types'

export const PRESETS: Preset[] = [
  {
    id: 'alice-stipend',
    label: '1 · Alice authorized',
    principalId: 'alice_hr',
    question: 'What is the monthly home-office stipend for fully remote employees?',
    expect: 'Answer + cite POL-HR-001 ($75)',
  },
  {
    id: 'bob-denied',
    label: '2 · Bob ACL deny',
    principalId: 'bob_eng',
    question: 'What is the monthly home-office stipend for fully remote employees?',
    expect: 'Refuse — confidential HR filtered',
  },
  {
    id: 'eve-public',
    label: '3 · Eve public',
    principalId: 'eve_contractor',
    question: 'How do I report harassment or ethics concerns?',
    expect: 'Answer + cite POL-PUB-003',
  },
  {
    id: 'fabricate',
    label: '4 · No fabricate',
    principalId: 'alice_hr',
    question: 'What is our pet-friendly office aquarium cleaning schedule?',
    expect: 'Refuse — no corpus evidence',
  },
]
