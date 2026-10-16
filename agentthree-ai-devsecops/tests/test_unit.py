"""Basic unit checks for gate helpers."""

from agentthree_devsecops.evaluation import DEFAULT_THRESHOLDS, score_fixture
from agentthree_devsecops.rollback import simulate_health_check


def test_health_check_threshold():
    assert simulate_health_check(0.01) is True
    assert simulate_health_check(0.081) is False


def test_score_fixture_pass():
    result = score_fixture(
        {
            "id": "t",
            "metrics": {
                "grounding": 0.95,
                "faithfulness": 0.95,
                "prompt_injection_pass_rate": 1.0,
                "unsafe_tool_use": 0,
            },
        },
        DEFAULT_THRESHOLDS,
    )
    assert result["passed"] is True


def test_score_fixture_fail_grounding():
    result = score_fixture(
        {
            "id": "t",
            "metrics": {
                "grounding": 0.82,
                "faithfulness": 0.95,
                "prompt_injection_pass_rate": 1.0,
                "unsafe_tool_use": 0,
            },
        },
        DEFAULT_THRESHOLDS,
    )
    assert result["passed"] is False
    assert result["checks"]["grounding"] is False
