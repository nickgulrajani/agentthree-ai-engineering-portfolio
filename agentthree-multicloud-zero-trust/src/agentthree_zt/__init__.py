"""AgentThree multi-cloud zero trust for AI agents (zero-billing local runtime)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "trust.json"
POLICY_DIR = ROOT / "policy"
RECORDS_PATH = ROOT / "data" / "records.json"
