"""Rollback procedure dry-run — restores previous revision in the local manifest only."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def simulate_health_check(error_rate: float, threshold: float = 0.02) -> bool:
    return error_rate <= threshold


def rollback(manifest_path: Path, out_path: Path, error_rate: float) -> int:
    if not manifest_path.exists():
        print(f"missing deploy manifest: {manifest_path}", file=sys.stderr)
        return 2

    manifest = json.loads(manifest_path.read_text())
    healthy = simulate_health_check(error_rate)
    action = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "dry-run",
        "observed_error_rate": error_rate,
        "threshold": 0.02,
        "health_ok": healthy,
        "from_revision": manifest.get("revision"),
        "to_revision": manifest.get("previous_revision"),
        "cloud_apply": False,
    }

    if healthy:
        action["result"] = "healthy — no rollback"
        print(json.dumps(action, indent=2))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(action, indent=2))
        return 0

    action["result"] = "ROLLBACK initiated (simulated)"
    action["restored_revision"] = manifest.get("previous_revision")
    print(json.dumps(action, indent=2))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(action, indent=2))
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Health check + rollback dry-run")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("artifacts/deploy-manifest.json"),
    )
    parser.add_argument("--error-rate", type=float, default=0.0)
    parser.add_argument("--out", type=Path, default=Path("artifacts/rollback-result.json"))
    args = parser.parse_args(argv)
    return rollback(args.manifest, args.out, args.error_rate)


if __name__ == "__main__":
    raise SystemExit(main())
