"""Regression gate pass/fail behavior."""

from agentthree_agent_eval.gate import GateThresholds, evaluate_gate
from agentthree_agent_eval.metrics import run_suite
from agentthree_agent_eval.simulate import AgentConfig


def test_default_candidate_clears_gate():
    baseline = run_suite(AgentConfig(model="medium", plan="none", desc="terse"), trials=3, seed=7)
    candidate = run_suite(AgentConfig(model="medium", plan="plan", desc="detailed"), trials=3, seed=7)
    result = evaluate_gate(baseline, candidate)
    assert result.passed, [c for c in result.checks if not c.passed]


def test_impossible_thresholds_fail():
    baseline = run_suite(AgentConfig(), trials=1, seed=3)
    candidate = run_suite(AgentConfig(plan="plan", desc="detailed"), trials=1, seed=3)
    result = evaluate_gate(
        baseline,
        candidate,
        GateThresholds(min_success=0.99, max_p95_latency=0.01, max_cost_per_task=0.0001),
        enforce_no_category_regression=False,
    )
    assert not result.passed
