"""End-to-end evaluation gate against committed fixtures."""

from pathlib import Path

from agentthree_devsecops.evaluation import load_thresholds, run_eval

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "evaluation" / "fixtures"
THRESHOLDS = ROOT / "evaluation" / "thresholds.yaml"


def test_pass_fixture_allows_promotion(tmp_path):
    code = run_eval(
        FIXTURES / "pass_grounding.json",
        THRESHOLDS,
        tmp_path / "pass.json",
    )
    assert code == 0


def test_fail_fixture_blocks_promotion(tmp_path):
    code = run_eval(
        FIXTURES / "fail_grounding.json",
        THRESHOLDS,
        tmp_path / "fail.json",
    )
    assert code == 1


def test_thresholds_loaded():
    t = load_thresholds(THRESHOLDS)
    assert t["grounding_min"] == 0.90
