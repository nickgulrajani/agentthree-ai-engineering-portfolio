"""Deployment dry-run + approval gate. Never touches a cloud provider."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def require_approval(approved: bool | None = None) -> None:
    """Block promotion unless explicit approval is present."""
    if approved is None:
        flag = os.environ.get("PROD_APPROVED", "").strip().lower()
        approved = flag in {"1", "true", "yes", "approved"}
    if not approved:
        raise SystemExit(
            "DEPLOY BLOCKED: production approval missing. "
            "Set PROD_APPROVED=true (local demo) or use a GitHub Environment approval."
        )


def write_manifest(
    out: Path,
    *,
    target: str,
    digest: str,
    revision: str,
    previous_revision: str,
) -> dict:
    manifest = {
        "mode": "dry-run",
        "target": target,
        "artifact_digest": digest,
        "revision": revision,
        "previous_revision": previous_revision,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cloud_apply": False,
        "note": "No infrastructure or workload was deployed.",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2))
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run deploy with optional approval gate")
    parser.add_argument("--target", default="prod", choices=["dev", "test", "prod"])
    parser.add_argument("--digest", default="sha256:demo-7f29")
    parser.add_argument("--revision", default="rev-002")
    parser.add_argument("--previous-revision", default="rev-001")
    parser.add_argument("--require-approval", action="store_true")
    parser.add_argument("--out", type=Path, default=Path("artifacts/deploy-manifest.json"))
    args = parser.parse_args(argv)

    if args.require_approval or args.target == "prod":
        require_approval()

    manifest = write_manifest(
        args.out,
        target=args.target,
        digest=args.digest,
        revision=args.revision,
        previous_revision=args.previous_revision,
    )
    print(f"DRY-RUN deploy → {args.target}")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
