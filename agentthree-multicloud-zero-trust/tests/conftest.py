"""Shared fixtures. Integration tests require the OPA binary on PATH."""

from __future__ import annotations

import shutil

import pytest

from agentthree_zt.agents import Environment

OPA_INSTALL_HINT = (
    "OPA binary not found — skipping allow/deny integration tests.\n"
    "Install OPA, then re-run pytest / make verify:\n"
    "  macOS:  brew install opa\n"
    "  Linux:  curl -L -o opa "
    "https://openpolicyagent.org/downloads/latest/opa_linux_amd64_static "
    "&& chmod +x opa && sudo mv opa /usr/local/bin/opa\n"
    "  Docs:   https://www.openpolicyagent.org/docs/latest/#running-opa"
)


@pytest.fixture(scope="session", autouse=True)
def require_opa_binary() -> None:
    if not shutil.which("opa"):
        pytest.skip(OPA_INSTALL_HINT)


@pytest.fixture
def env(tmp_path):
    return Environment(audit_path=tmp_path / "audit.jsonl")
