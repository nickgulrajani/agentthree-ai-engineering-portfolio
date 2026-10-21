"""Coverage, unit cost, and showback against the HTML lab fixtures."""

from __future__ import annotations

from agentthree_aws_finops.engine import load_state


def test_starting_coverage_is_61_percent() -> None:
    state = load_state()
    assert round(state.coverage, 2) == 0.61
    assert round(state.unallocated_k, 1) == 161.0
    assert round(state.unit_cost_per_1k, 2) == 2.58


def test_tag_all_reaches_coverage_target() -> None:
    state = load_state()
    applied = state.apply_tags()
    assert applied == 9
    assert state.coverage >= state.coverage_target
    assert round(state.coverage, 2) == 0.91
    assert round(state.unallocated_k, 1) == 37.0


def test_showback_moves_spend_to_owning_team() -> None:
    state = load_state()
    before = state.showback()
    state.apply_tags()
    after = state.showback()
    assert after["Platform"] > before["Platform"]
    assert after["Fraud & Risk"] > before["Fraud & Risk"]
    assert after["Unallocated"] == 37.0
