"""Savings backlog over fixture recommendations. Selecting recs does not call AWS."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Recommendation:
    id: str
    category: str
    title: str
    monthly_k: float
    default_on: bool
    selected: bool = False


def load_recommendations(path: Path | None = None) -> list[Recommendation]:
    raw = yaml.safe_load((path or ROOT / "data" / "recommendations.yaml").read_text())
    recs = []
    for item in raw["recommendations"]:
        rec = Recommendation(
            id=item["id"],
            category=item["category"],
            title=item["title"],
            monthly_k=float(item["monthly_k"]),
            default_on=bool(item["default_on"]),
        )
        rec.selected = rec.default_on
        recs.append(rec)
    return recs


def apply_selection(recs: list[Recommendation], ids: list[str] | None) -> list[Recommendation]:
    if ids is None:
        return recs
    wanted = set(ids)
    if "all" in wanted:
        for rec in recs:
            rec.selected = True
        return recs
    for rec in recs:
        rec.selected = rec.id in wanted
    return recs


def monthly_savings_k(recs: list[Recommendation]) -> float:
    return sum(r.monthly_k for r in recs if r.selected)


def projected_run_rate_k(monthly_spend_k: float, recs: list[Recommendation]) -> float:
    return round(monthly_spend_k - monthly_savings_k(recs), 1)


def unit_cost_after(monthly_spend_k: float, transactions: int, recs: list[Recommendation]) -> float:
    projected = projected_run_rate_k(monthly_spend_k, recs) * 1000.0
    return projected / transactions * 1000.0
