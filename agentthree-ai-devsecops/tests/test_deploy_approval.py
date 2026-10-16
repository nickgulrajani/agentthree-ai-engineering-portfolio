"""Approval and rollback dry-run behavior."""

import json
from pathlib import Path

import pytest

from agentthree_devsecops import deploy_dry_run, rollback


def test_prod_blocked_without_approval(monkeypatch, tmp_path):
    monkeypatch.delenv("PROD_APPROVED", raising=False)
    with pytest.raises(SystemExit) as exc:
        deploy_dry_run.main(
            [
                "--target",
                "prod",
                "--out",
                str(tmp_path / "m.json"),
            ]
        )
    assert "DEPLOY BLOCKED" in str(exc.value)


def test_prod_allowed_with_approval(monkeypatch, tmp_path):
    monkeypatch.setenv("PROD_APPROVED", "true")
    out = tmp_path / "m.json"
    code = deploy_dry_run.main(["--target", "prod", "--out", str(out)])
    assert code == 0
    data = json.loads(out.read_text())
    assert data["cloud_apply"] is False
    assert data["previous_revision"] == "rev-001"


def test_rollback_on_high_error_rate(tmp_path):
    manifest = tmp_path / "deploy-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "revision": "rev-002",
                "previous_revision": "rev-001",
                "mode": "dry-run",
            }
        )
    )
    out = tmp_path / "rollback.json"
    code = rollback.main(
        ["--manifest", str(manifest), "--error-rate", "0.081", "--out", str(out)]
    )
    assert code == 1
    result = json.loads(out.read_text())
    assert result["restored_revision"] == "rev-001"
