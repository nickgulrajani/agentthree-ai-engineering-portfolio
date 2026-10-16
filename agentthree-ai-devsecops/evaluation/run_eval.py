#!/usr/bin/env python3
"""CLI entry for offline agent evaluation (delegates to package)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentthree_devsecops.evaluation import main

if __name__ == "__main__":
    raise SystemExit(main())
