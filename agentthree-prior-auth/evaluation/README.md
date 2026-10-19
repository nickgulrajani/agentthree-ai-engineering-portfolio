# Evaluation

Synthetic prior-auth cases scored on **outcome accuracy** (meets / pend / urgent).

```bash
.venv/bin/python -m evaluation.run_eval
```

| File | Purpose |
|------|---------|
| `cases.json` | Golden scenarios (5 cases) for CPT 72148 / AHP-RAD-014 |
| `run_eval.py` | Deterministic scorer (domain helpers; no Gemini required) |
| `published_results.json` | **Committed** baseline metrics for recruiters / CI drift checks |
| `last_results.json` | Latest local run (gitignored) — shown in the UI Evaluation tab when present |

## UI

The React **Evaluation** tab loads `GET /api/evaluation` (published baseline, plus `last_results.json` when you re-run the scorer).

## Published results

See [`published_results.json`](./published_results.json) for the committed baseline (`outcome_accuracy`, per-case pass/fail). Re-run `python -m evaluation.run_eval` after changing `cases.json` or domain logic, then refresh the published file if the baseline should move.

## Metrics (roadmap)

Expand beyond outcome accuracy: documentation completeness, criterion match, citation grounding, escalation correctness, latency budgets.
