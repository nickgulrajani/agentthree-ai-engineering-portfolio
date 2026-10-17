"""Regression gate: ship candidate only if thresholds and category deltas hold."""

from __future__ import annotations

from dataclasses import dataclass

from .metrics import Scorecard
from .tasks import CATEGORIES


@dataclass(frozen=True)
class GateThresholds:
    min_success: float = 0.70
    max_p95_latency: float = 16.0
    max_cost_per_task: float = 0.08
    max_category_regression: float = 0.05  # 5 pts


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


@dataclass
class GateResult:
    passed: bool
    checks: list[Check]


def evaluate_gate(
    baseline: Scorecard,
    candidate: Scorecard,
    thresholds: GateThresholds | None = None,
    *,
    enforce_no_category_regression: bool = True,
) -> GateResult:
    t = thresholds or GateThresholds()
    checks = [
        Check(
            f"Task success ≥ {t.min_success:.0%}",
            candidate.success >= t.min_success,
            f"{candidate.success:.1%}",
        ),
        Check(
            f"p95 latency ≤ {t.max_p95_latency:.1f}s",
            candidate.p95_latency <= t.max_p95_latency,
            f"{candidate.p95_latency:.1f}s",
        ),
        Check(
            f"Cost / task ≤ ${t.max_cost_per_task:.3f}",
            candidate.cost_per_task <= t.max_cost_per_task,
            f"${candidate.cost_per_task:.4f}",
        ),
    ]
    if enforce_no_category_regression:
        worst_name = ""
        worst_delta = 0.0
        for cat in CATEGORIES:
            k = cat["k"]
            delta = candidate.by_category[k].success - baseline.by_category[k].success
            if not worst_name or delta < worst_delta:
                worst_name, worst_delta = cat["n"], delta
        checks.append(
            Check(
                f"No category regresses > {t.max_category_regression * 100:.0f} pts",
                worst_delta >= -t.max_category_regression,
                f"worst: {worst_name} {worst_delta * 100:+.1f} pts",
            )
        )
    return GateResult(passed=all(c.passed for c in checks), checks=checks)
