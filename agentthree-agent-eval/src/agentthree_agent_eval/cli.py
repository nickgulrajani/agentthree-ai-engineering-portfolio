"""CLI: compare baseline vs candidate and print the regression gate."""

from __future__ import annotations

import json
from pathlib import Path

import click
import yaml

from .gate import GateThresholds, evaluate_gate
from .metrics import run_suite
from .simulate import AgentConfig
from .tasks import TASKS


def _load_thresholds(path: Path | None) -> GateThresholds:
    if path is None or not path.exists():
        return GateThresholds()
    data = yaml.safe_load(path.read_text()) or {}
    return GateThresholds(
        min_success=float(data.get("min_success", 0.70)),
        max_p95_latency=float(data.get("max_p95_latency", 16.0)),
        max_cost_per_task=float(data.get("max_cost_per_task", 0.08)),
        max_category_regression=float(data.get("max_category_regression", 0.05)),
    )


@click.command()
@click.option("--trials", default=3, show_default=True, help="Trials per task")
@click.option("--seed", default=7, show_default=True)
@click.option(
    "--thresholds",
    "thresholds_path",
    type=click.Path(path_type=Path),
    default=None,
    help="YAML gate thresholds",
)
@click.option("--json-out", is_flag=True, help="Emit machine-readable JSON")
def main(trials: int, seed: int, thresholds_path: Path | None, json_out: bool) -> None:
    """Run the 40-task suite for baseline A vs candidate B and apply the gate."""
    baseline_cfg = AgentConfig(model="medium", plan="none", desc="terse", retry=True)
    candidate_cfg = AgentConfig(model="medium", plan="plan", desc="detailed", retry=True)
    a = run_suite(baseline_cfg, trials=trials, seed=seed)
    b = run_suite(candidate_cfg, trials=trials, seed=seed)
    gate = evaluate_gate(a, b, _load_thresholds(thresholds_path))

    if json_out:
        payload = {
            "tasks": len(TASKS),
            "trials": trials,
            "seed": seed,
            "baseline": {
                "success": a.success,
                "consistency": a.consistency,
                "tool_accuracy": a.tool_accuracy,
                "p95_latency": a.p95_latency,
                "cost_per_task": a.cost_per_task,
            },
            "candidate": {
                "success": b.success,
                "consistency": b.consistency,
                "tool_accuracy": b.tool_accuracy,
                "p95_latency": b.p95_latency,
                "cost_per_task": b.cost_per_task,
            },
            "gate": {"passed": gate.passed, "checks": [c.__dict__ for c in gate.checks]},
        }
        click.echo(json.dumps(payload, indent=2))
    else:
        click.echo(f"Suite: {len(TASKS)} tasks × {trials} trials × 2 configs (seed={seed})")
        click.echo(
            f"A baseline  success={a.success:.1%}  pass^{trials}={a.consistency:.1%}  "
            f"tool={a.tool_accuracy:.1%}  p95={a.p95_latency:.1f}s  cost=${a.cost_per_task:.4f}"
        )
        click.echo(
            f"B candidate success={b.success:.1%}  pass^{trials}={b.consistency:.1%}  "
            f"tool={b.tool_accuracy:.1%}  p95={b.p95_latency:.1f}s  cost=${b.cost_per_task:.4f}"
        )
        click.echo("")
        click.echo("PASS — ship B" if gate.passed else "FAIL — keep A")
        for c in gate.checks:
            mark = "✓" if c.passed else "✗"
            click.echo(f"  {mark} {c.name}  ({c.detail})")

    raise SystemExit(0 if gate.passed else 1)


if __name__ == "__main__":
    main()
