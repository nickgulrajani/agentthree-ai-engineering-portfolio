# Agent evaluation architecture

```text
┌──────────────────┐     ┌─────────────────────┐
│ 40-task suite    │────▶│ Seeded simulator     │
│ 5 categories     │     │ model · plan · desc  │
└──────────────────┘     └──────────┬──────────┘
                                    │ trajectories
                                    ▼
                         ┌─────────────────────┐
                         │ Scorecard            │
                         │ success · pass^k     │
                         │ tool/arg · p95 · $   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Regression gate      │
                         │ thresholds.yaml      │
                         └─────────────────────┘
```

Production mapping: replace the simulator with recorded or live agent traces; keep the same scorecard fields and gate thresholds in CI.
