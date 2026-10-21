"""Policy gates on fixture Terraform plans — Python path (always runs)."""

from __future__ import annotations

from pathlib import Path

from agentthree_aws_finops.policy import gate, load_json

ROOT = Path(__file__).resolve().parents[1]
PLANS = ROOT / "data" / "plans"


def test_untagged_plan_fails() -> None:
    status, findings = gate(load_json(PLANS / "deny_untagged.json"))
    assert status == "FAIL"
    rules = {f.rule for f in findings}
    assert "terraform.tags" in rules
    assert "terraform.tag_values" in rules
    assert "terraform.instance_size" in rules


def test_fully_tagged_plan_passes() -> None:
    status, findings = gate(load_json(PLANS / "allow_tagged.json"))
    assert status == "PASS"
    assert findings == []


def test_infracost_diff_warns_without_failing() -> None:
    status, findings = gate(
        load_json(PLANS / "allow_tagged.json"),
        load_json(PLANS / "infracost_warn.json"),
    )
    assert status == "WARN"
    assert any(f.rule == "infracost" and f.severity == "warn" for f in findings)
    assert not any(f.severity == "deny" for f in findings)
