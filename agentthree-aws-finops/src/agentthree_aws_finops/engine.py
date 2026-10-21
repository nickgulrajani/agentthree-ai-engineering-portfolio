"""CUR-shaped FinOps math over fixture data. No AWS APIs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Team:
    name: str
    base_k: float


@dataclass
class UntaggedResource:
    name: str
    meta: str
    account: str
    team: str
    why: str
    cost_k: float
    missing: list[str]
    tagged: bool = False


@dataclass
class FinOpsState:
    monthly_spend_k: float
    transactions: int
    untagged_pool_k: float
    shared_after_tagging_k: float
    coverage_target: float
    teams: list[Team]
    resources: list[UntaggedResource]
    trend_k: list[dict[str, Any]] = field(default_factory=list)
    services_k: dict[str, float] = field(default_factory=dict)

    @property
    def tagged_k(self) -> float:
        return sum(r.cost_k for r in self.resources if r.tagged)

    @property
    def unallocated_k(self) -> float:
        remaining = self.untagged_pool_k - self.tagged_k
        if remaining <= self.shared_after_tagging_k and all(r.tagged for r in self.resources):
            return self.shared_after_tagging_k
        return remaining

    @property
    def allocated_k(self) -> float:
        return self.monthly_spend_k - self.unallocated_k

    @property
    def coverage(self) -> float:
        return self.allocated_k / self.monthly_spend_k

    @property
    def unit_cost_per_1k(self) -> float:
        monthly_usd = self.monthly_spend_k * 1000.0
        return monthly_usd / self.transactions * 1000.0

    def showback(self) -> dict[str, float]:
        by_team = {t.name: t.base_k for t in self.teams}
        for resource in self.resources:
            if resource.tagged:
                by_team[resource.team] = by_team.get(resource.team, 0.0) + resource.cost_k
        by_team["Unallocated"] = self.unallocated_k
        return by_team

    def apply_tags(self, names: list[str] | None = None) -> int:
        applied = 0
        for resource in self.resources:
            if resource.tagged:
                continue
            if names is None or resource.name in names:
                resource.tagged = True
                applied += 1
        return applied


def load_state(
    config_path: Path | None = None,
    untagged_path: Path | None = None,
) -> FinOpsState:
    cfg = yaml.safe_load((config_path or ROOT / "configs" / "finops.yaml").read_text())
    rows = yaml.safe_load((untagged_path or ROOT / "data" / "untagged.yaml").read_text())
    return FinOpsState(
        monthly_spend_k=float(cfg["monthly_spend_k"]),
        transactions=int(cfg["transactions"]),
        untagged_pool_k=float(cfg["untagged_pool_k"]),
        shared_after_tagging_k=float(cfg["shared_after_tagging_k"]),
        coverage_target=float(cfg["coverage_target"]),
        teams=[Team(**t) for t in cfg["teams"]],
        resources=[
            UntaggedResource(
                name=r["name"],
                meta=r["meta"],
                account=r["account"],
                team=r["team"],
                why=r["why"],
                cost_k=float(r["cost_k"]),
                missing=list(r["missing"]),
            )
            for r in rows["resources"]
        ],
        trend_k=list(cfg.get("trend_k") or []),
        services_k=dict(cfg.get("services_k") or {}),
    )
