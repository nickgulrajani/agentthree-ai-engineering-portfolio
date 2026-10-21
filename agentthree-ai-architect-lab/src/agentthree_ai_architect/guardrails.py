from __future__ import annotations

import re

PII = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL]"),
    (re.compile(r"\(?\b\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"), "[PHONE]"),
]
INJECTION = re.compile(
    r"ignore (all |any |the )?(previous|prior|above) (instructions|rules)|"
    r"reveal (your )?system prompt|"
    r"you are now|"
    r"disregard (your|all) (rules|instructions)",
    re.I,
)
PROTECTED_RE = re.compile(
    r"\b(race|religion|religious|national origin|marital status|pregnan\w*|ethnicity)\b",
    re.I,
)
PROTECTED = [
    "race",
    "religion",
    "sex",
    "national_origin",
    "marital_status",
    "age",
]


def redact_pii(text: str) -> tuple[str, int]:
    count = 0
    redacted = text
    for pattern, repl in PII:

        def _sub(_m: re.Match[str], r: str = repl) -> str:
            nonlocal count
            count += 1
            return r

        redacted = pattern.sub(_sub, redacted)
    return redacted, count


def is_injection(text: str) -> bool:
    return bool(INJECTION.search(text))


def mentions_protected(text: str) -> bool:
    return bool(PROTECTED_RE.search(text))
