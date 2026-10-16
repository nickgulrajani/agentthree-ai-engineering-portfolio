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
| `last_results.json` | Latest local run (gitignored) — paste into the UI Evaluation tab |

## Published results

See [`published_results.json`](./published_results.json) for the committed baseline (`outcome_accuracy`, per-case pass/fail). Re-run `python -m evaluation.run_eval` after changing `cases.json` or domain logic, then refresh the published file if the baseline should move.

## Metrics (roadmap)

Align with the Live Run Evaluation tab: documentation completeness, criterion match, citation grounding, escalation correctness, latency budgets.
