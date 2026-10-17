"""Scorecard metrics stay in range and improve with better configs."""

from agentthree_agent_eval.metrics import run_suite
from agentthree_agent_eval.simulate import AgentConfig


def test_scorecard_bounds():
    card = run_suite(AgentConfig(), trials=1, seed=7)
    assert 0.0 <= card.success <= 1.0
    assert 0.0 <= card.tool_accuracy <= 1.0
    assert card.p95_latency >= card.p50_latency
    assert card.cost_per_task > 0
    assert set(card.by_category) == {"status", "refund", "billing", "trouble", "adv"}


def test_detailed_descriptions_raise_tool_accuracy():
    terse = run_suite(AgentConfig(desc="terse", plan="none"), trials=2, seed=11)
    detailed = run_suite(AgentConfig(desc="detailed", plan="none"), trials=2, seed=11)
    assert detailed.tool_accuracy >= terse.tool_accuracy - 1e-9
