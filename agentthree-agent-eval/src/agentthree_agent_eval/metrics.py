"""Scorecard metrics over the fixed task suite."""

from __future__ import annotations

from dataclasses import dataclass, field

from .simulate import AgentConfig, TrialResult, simulate_task
from .tasks import CATEGORIES, TASKS, Task


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, int(p * len(ordered)))
    return ordered[idx]


@dataclass
class CategoryScore:
    success: float
    n: int


@dataclass
class Scorecard:
    trials_per_task: int
    success: float
    consistency: float
    tool_accuracy: float
    arg_accuracy: float
    p50_latency: float
    p95_latency: float
    cost_per_task: float
    cost_per_success: float
    by_category: dict[str, CategoryScore] = field(default_factory=dict)
    rows: list[tuple[Task, list[TrialResult]]] = field(default_factory=list, repr=False)


def run_suite(
    cfg: AgentConfig,
    *,
    trials: int = 3,
    seed: int = 7,
    tasks: list[Task] | None = None,
) -> Scorecard:
    suite = tasks if tasks is not None else TASKS
    rows: list[tuple[Task, list[TrialResult]]] = []
    succ = all_n = tool_ok = tool_all = arg_ok = arg_all = consist = 0
    lats: list[float] = []
    cost = 0.0

    for task in suite:
        trials_out = [simulate_task(cfg, task, seed=seed, trial=k) for k in range(trials)]
        rows.append((task, trials_out))
        if all(t.ok for t in trials_out):
            consist += 1
        for trial in trials_out:
            all_n += 1
            if trial.ok:
                succ += 1
            lats.append(trial.latency)
            cost += trial.cost
            called = [s for s in trial.steps if s.status != "miss"]
            expected = len(task.trajectory)
            if expected:
                tool_all += max(expected, len([s for s in called if s.tool != "refuse"])) or 1
                tool_ok += sum(1 for s in trial.steps if s.status in ("ok", "args"))
            else:
                tool_all += 1
                tool_ok += 1 if trial.ok else 0
            arg_steps = [s for s in trial.steps if (s.status == "ok" and s.tool != "refuse") or s.status == "args"]
            arg_all += len(arg_steps)
            arg_ok += sum(1 for s in trial.steps if s.status == "ok" and s.tool != "refuse") - sum(
                1 for s in trial.steps if s.fixed
            )

    by_cat: dict[str, CategoryScore] = {}
    for cat in CATEGORIES:
        cat_rows = [(t, tr) for t, tr in rows if t.category == cat["k"]]
        n = len(cat_rows) * trials
        s = sum(1 for _, tr in cat_rows for x in tr if x.ok)
        by_cat[cat["k"]] = CategoryScore(success=(s / n if n else 0.0), n=n)

    return Scorecard(
        trials_per_task=trials,
        success=succ / all_n if all_n else 0.0,
        consistency=consist / len(rows) if rows else 0.0,
        tool_accuracy=tool_ok / tool_all if tool_all else 0.0,
        arg_accuracy=arg_ok / arg_all if arg_all else 1.0,
        p50_latency=_percentile(lats, 0.5),
        p95_latency=_percentile(lats, 0.95),
        cost_per_task=cost / all_n if all_n else 0.0,
        cost_per_success=(cost / succ) if succ else float("inf"),
        by_category=by_cat,
        rows=rows,
    )
