"""Seeded agent simulator — same model/planning knobs as the browser lab."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .tasks import ALL_TOOLS, Task


MODELS = {
    "small": {"n": "Small (fast)", "skill": 0.66, "guard": 0.55, "lat": 0.55, "price": 0.4},
    "medium": {"n": "Medium", "skill": 0.80, "guard": 0.75, "lat": 1.15, "price": 3.5},
    "large": {"n": "Large (frontier)", "skill": 0.90, "guard": 0.90, "lat": 2.3, "price": 15.0},
}


@dataclass
class AgentConfig:
    model: str = "medium"
    plan: str = "none"  # none | plan | reflect
    desc: str = "terse"  # terse | detailed
    retry: bool = True
    max_steps: int = 8


@dataclass
class Step:
    status: str  # ok | wrong | args | extra | err | miss
    tool: str
    fixed: bool = False


@dataclass
class TrialResult:
    ok: bool
    steps: list[Step]
    turns: int
    tokens: int
    latency: float
    cost: float


def _mulberry32(seed: int) -> Callable[[], float]:
    state = seed & 0xFFFFFFFF

    def rng() -> float:
        nonlocal state
        state = (state + 0x6D2B79F5) & 0xFFFFFFFF
        t = state
        t = (t ^ (t >> 15)) & 0xFFFFFFFF
        t = (t * (1 | t)) & 0xFFFFFFFF
        t ^= (t + ((t * ((t ^ (t >> 7)) & 0xFFFFFFFF) * 61) & 0xFFFFFFFF)) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296.0

    return rng


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def simulate_task(
    cfg: AgentConfig,
    task: Task,
    *,
    seed: int = 7,
    trial: int = 0,
) -> TrialResult:
    """Run one seeded trial for a task under an agent configuration."""
    # Decision RNG is independent of latency noise so planning turns do not
    # scramble adversarial / tool-selection outcomes across configs.
    R = _mulberry32((task.id * 2654435761) ^ (trial * 97531) ^ (seed * 1013904223))
    R_lat = _mulberry32((task.id * 2246822519) ^ (trial * 3266489917) ^ (seed * 668265263))
    M = MODELS[cfg.model]
    detailed = cfg.desc == "detailed"
    multi = len(task.trajectory) >= 3
    skill = M["skill"]
    if cfg.plan == "plan" and multi:
        skill += 0.05
    elif cfg.plan == "reflect":
        skill += 0.08 if multi else 0.03
    recover = 0.6 if cfg.plan == "reflect" else (0.3 if cfg.plan == "plan" else 0.12)

    steps: list[Step] = []
    ok = True
    turns = 1
    tokens = 0
    latency = 0.0

    def turn(n: int = 1) -> None:
        nonlocal turns, tokens, latency
        for _ in range(n):
            turns += 1
            t = 900 + turns * 380 * (1.4 if cfg.plan == "reflect" else 1.0)
            tokens += int(t)
            latency += M["lat"] * (1.35 if cfg.plan == "reflect" else 1.0) * (0.8 + R_lat() * 0.5)

    if cfg.plan != "none":
        turn(1)

    if not task.trajectory:
        guard = _clamp(
            M["guard"] + (0.05 if detailed else 0) + (0.06 if cfg.plan == "reflect" else 0) - task.difficulty * 0.15,
            0.0,
            0.99,
        )
        turn(1)
        if R() < guard:
            steps.append(Step("ok", "refuse"))
        else:
            ok = False
            wrong = ["issue_refund", "lookup_customer", "create_ticket"][int(R() * 3)]
            steps.append(Step("wrong", wrong))
    else:
        for k, tool in enumerate(task.trajectory):
            if not ok:
                break
            turn(1)
            latency += 0.35 + R_lat() * 0.3
            sel = _clamp(1 - (1 - skill) * (0.45 + task.difficulty * 0.55) * (0.5 if detailed else 1.0), 0.05, 0.998)
            if R() > sel:
                others = [t for t in ALL_TOOLS if t != tool]
                wrong = others[int(R() * (len(others)))]
                steps.append(Step("wrong", wrong))
                if R() < recover:
                    turn(1)
                    latency += 0.4
                else:
                    ok = False
                    for miss in task.trajectory[k:]:
                        steps.append(Step("miss", miss))
                    break
            if R() < 0.08:
                steps.append(Step("err", tool))
                if cfg.retry:
                    turn(1)
                    latency += 0.8
                else:
                    ok = False
                    for miss in task.trajectory[k + 1 :]:
                        steps.append(Step("miss", miss))
                    break
            argp = _clamp(1 - (1 - skill) * (0.15 + task.difficulty * 0.3) * (0.7 if detailed else 1.0), 0.05, 0.998)
            if R() > argp:
                if cfg.plan == "reflect" and R() < 0.5:
                    steps.append(Step("args", tool, fixed=True))
                    turn(1)
                    latency += 0.4
                    steps.append(Step("ok", tool))
                else:
                    steps.append(Step("args", tool))
                    ok = False
                    for miss in task.trajectory[k + 1 :]:
                        steps.append(Step("miss", miss))
                    break
            else:
                steps.append(Step("ok", tool))
            if R() < 0.1 * (1.1 - skill):
                steps.append(Step("extra", ALL_TOOLS[int(R() * len(ALL_TOOLS))]))
                turn(1)
                latency += 0.4
            if turns > cfg.max_steps:
                ok = False
                steps.append(Step("miss", "⟂ max steps"))
                break

    turn(1)
    cost = tokens * M["price"] / 1e6
    return TrialResult(ok=ok, steps=steps, turns=turns, tokens=tokens, latency=latency, cost=cost)
