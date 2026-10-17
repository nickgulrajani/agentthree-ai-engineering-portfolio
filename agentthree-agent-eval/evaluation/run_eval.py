#!/usr/bin/env python3
"""Published eval entrypoint used by portfolio `make verify`."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentthree_agent_eval.cli import main

if __name__ == "__main__":
    # Defaults: seed=7, trials=3, thresholds.yaml next to this file
    sys.argv = [
        "run_eval",
        "--trials",
        "3",
        "--seed",
        "7",
        "--thresholds",
        str(Path(__file__).with_name("thresholds.yaml")),
    ]
    main()
