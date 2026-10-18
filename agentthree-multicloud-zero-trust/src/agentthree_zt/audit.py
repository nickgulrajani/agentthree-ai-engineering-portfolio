"""Append-only, hash-chained audit log. Any edit or deletion breaks the chain."""

import hashlib
import json
from pathlib import Path

GENESIS = "0" * 64


def _digest(prev: str, event: dict) -> str:
    body = json.dumps(event, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256((prev + body).encode()).hexdigest()


class AuditLog:
    def __init__(self, path: Path | None = None, clock=None):
        self.path = path
        self.clock = clock
        self.entries: list[dict] = []
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            # Append + resume: never truncate an existing hash chain on startup.
            if path.exists() and path.stat().st_size > 0:
                self.entries = load(path)
            else:
                path.touch(exist_ok=True)

    def record(self, component: str, action: str, principal: str, decision: str, **details) -> dict:
        prev = self.entries[-1]["hash"] if self.entries else GENESIS
        event = {
            "seq": len(self.entries) + 1,
            "ts": self.clock.now() if self.clock else None,
            "component": component,
            "action": action,
            "principal": principal,
            "decision": decision,
            **details,
        }
        entry = {**event, "prev_hash": prev, "hash": _digest(prev, event)}
        self.entries.append(entry)
        if self.path:
            with self.path.open("a") as f:
                f.write(json.dumps(entry) + "\n")
        return entry

    def denials(self) -> list[dict]:
        return [e for e in self.entries if e["decision"] == "deny"]


def verify_chain(entries: list[dict]) -> tuple[bool, int | None]:
    """Return (ok, first_bad_seq)."""
    prev = GENESIS
    for e in entries:
        event = {k: v for k, v in e.items() if k not in ("prev_hash", "hash")}
        if e["prev_hash"] != prev or e["hash"] != _digest(prev, event):
            return False, e.get("seq")
        prev = e["hash"]
    return True, None


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
