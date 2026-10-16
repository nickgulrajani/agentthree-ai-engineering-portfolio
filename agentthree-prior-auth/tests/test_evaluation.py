"""Golden evaluation cases must all pass the deterministic domain scorer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agentthree.domain import cds_evaluate, evaluate_policy, extract_entities  # noqa: E402

CASES = json.loads((ROOT / "evaluation" / "cases.json").read_text())
PUBLISHED = ROOT / "evaluation" / "published_results.json"


def test_all_golden_cases_pass():
    failures = []
    for case in CASES:
        x = extract_entities(case["note"], case["icd"])
        pol = evaluate_policy(x)
        if pol["outcome"] != case["expected_outcome"]:
            failures.append(
                f"{case['id']}: expected={case['expected_outcome']} actual={pol['outcome']}"
            )
    assert not failures, failures


def test_cds_returns_grounded_recommendations():
    case = next(c for c in CASES if c["expected_outcome"] == "meets")
    x = extract_entities(case["note"], case["icd"])
    pol = evaluate_policy(x)
    cds = cds_evaluate(x, pol)
    assert cds["recs"]
    assert cds["grounding"]["unsupported"] == 0
    assert all(r.get("cite") for r in cds["recs"])


def test_published_results_match_current_scorer():
    assert PUBLISHED.is_file(), "commit evaluation/published_results.json"
    published = json.loads(PUBLISHED.read_text())
    rows = []
    for case in CASES:
        x = extract_entities(case["note"], case["icd"])
        pol = evaluate_policy(x)
        ok = pol["outcome"] == case["expected_outcome"]
        rows.append({"id": case["id"], "pass": ok, "actual": pol["outcome"]})
    passed = sum(1 for r in rows if r["pass"])
    total = len(rows)
    assert published["cases"] == total
    assert published["passed"] == passed
    assert published["outcome_accuracy"] == passed / total
