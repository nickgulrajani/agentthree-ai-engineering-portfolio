import pytest

from agentthree_zt.agents import Environment


@pytest.fixture
def env(tmp_path):
    return Environment(audit_path=tmp_path / "audit.jsonl")
