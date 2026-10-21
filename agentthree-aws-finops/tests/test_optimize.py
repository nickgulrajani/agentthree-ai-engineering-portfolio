"""Savings math matches the HTML lab 90-day outcome when all recs are selected."""

from __future__ import annotations

from agentthree_aws_finops.engine import load_state
from agentthree_aws_finops.optimize import (
    apply_selection,
    load_recommendations,
    monthly_savings_k,
    projected_run_rate_k,
    unit_cost_after,
)


def test_all_recommendations_match_html_outcome() -> None:
    state = load_state()
    recs = apply_selection(load_recommendations(), ["all"])
    assert round(monthly_savings_k(recs), 1) == 88.0
    assert projected_run_rate_k(state.monthly_spend_k, recs) == 324.8
    assert round(unit_cost_after(state.monthly_spend_k, state.transactions, recs), 2) == 2.03


def test_defaults_are_a_subset_of_the_backlog() -> None:
    recs = load_recommendations()
    selected = {r.id for r in recs if r.selected}
    assert selected == {"sp", "rs", "sch", "gp3", "orph"}
    assert monthly_savings_k(recs) < 88.0
