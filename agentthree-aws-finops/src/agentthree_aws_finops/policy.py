"""Evaluate Terraform-plan JSON the way OPA/Rego would — locally, no AWS."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = ("CostCenter", "Owner", "Environment", "Application")
ALLOWED_ENV = {"prod", "staging", "dev", "loadtest"}
CC_RE = re.compile(r"^CC-[0-9]{4}$")
NON_PROD_SIZES = {"nano", "micro", "small", "medium", "large", "xlarge", "2xlarge"}


@dataclass(frozen=True)
class Finding:
    severity: str  # deny | warn
    address: str
    rule: str
    message: str


def _after(rc: dict[str, Any]) -> dict[str, Any]:
    return dict((rc.get("change") or {}).get("after") or {})


def _tags(rc: dict[str, Any]) -> dict[str, str]:
    after = _after(rc)
    tags = after.get("tags_all") or after.get("tags") or {}
    return {str(k): str(v) for k, v in tags.items() if v is not None}


def _creates(plan: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for rc in plan.get("resource_changes") or []:
        actions = (rc.get("change") or {}).get("actions") or []
        if "create" in actions:
            out.append(rc)
    return out


def evaluate_plan(plan: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    for rc in _creates(plan):
        address = str(rc.get("address") or "unknown")
        rtype = str(rc.get("type") or "")
        after = _after(rc)
        tags = _tags(rc)

        if "tags" in after or "tags_all" in after:
            missing = [k for k in REQUIRED if k not in tags]
            if missing:
                findings.append(
                    Finding(
                        "deny",
                        address,
                        "terraform.tags",
                        f"{address} is missing required tags: {set(missing)}",
                    )
                )
            env = tags.get("Environment")
            if env and env not in ALLOWED_ENV:
                findings.append(
                    Finding(
                        "deny",
                        address,
                        "terraform.tag_values",
                        f"{address} has Environment={env!r}; allowed: {sorted(ALLOWED_ENV)}",
                    )
                )
            cc = tags.get("CostCenter")
            if cc and not CC_RE.match(cc):
                findings.append(
                    Finding(
                        "deny",
                        address,
                        "terraform.tag_values",
                        f"{address} has CostCenter={cc!r}; expected format CC-1234",
                    )
                )

        if rtype == "aws_instance":
            env = tags.get("Environment", "")
            itype = str(after.get("instance_type") or "")
            size = itype.split(".")[-1] if "." in itype else itype
            if env and env != "prod" and "SizeException" not in tags and size not in NON_PROD_SIZES:
                findings.append(
                    Finding(
                        "deny",
                        address,
                        "terraform.instance_size",
                        f"{address} uses {itype} in {env}; non-prod max is 2xlarge",
                    )
                )

        if rtype == "aws_ebs_volume" and after.get("type") == "gp2":
            findings.append(
                Finding(
                    "warn",
                    address,
                    "terraform.storage",
                    f"{address} uses gp2; gp3 is ~20% cheaper per GB",
                )
            )
    return findings


def evaluate_infracost(payload: dict[str, Any], review_usd: float = 1000, arch_usd: float = 5000) -> list[Finding]:
    findings: list[Finding] = []
    try:
        diff = float(payload.get("diffTotalMonthlyCost") or 0)
    except (TypeError, ValueError):
        diff = 0.0
    if diff > review_usd:
        findings.append(
            Finding(
                "warn",
                "infracost",
                "infracost",
                f"PR adds ${diff:.0f}/month (threshold ${review_usd:.0f}); FinOps review required",
            )
        )
    for project in payload.get("projects") or []:
        for resource in (project.get("breakdown") or {}).get("resources") or []:
            try:
                cost = float(resource.get("monthlyCost") or 0)
            except (TypeError, ValueError):
                cost = 0.0
            if cost > arch_usd:
                name = str(resource.get("name") or "resource")
                findings.append(
                    Finding(
                        "deny",
                        name,
                        "infracost",
                        f"{name} costs ${cost:.0f}/month; over ${arch_usd:.0f} needs architecture review",
                    )
                )
    return findings


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def gate(plan: dict[str, Any], infracost: dict[str, Any] | None = None) -> tuple[str, list[Finding]]:
    findings = evaluate_plan(plan)
    if infracost:
        cfg = yaml.safe_load((ROOT / "configs" / "finops.yaml").read_text())
        findings.extend(
            evaluate_infracost(
                infracost,
                review_usd=float(cfg.get("infracost_review_usd", 1000)),
                arch_usd=float(cfg.get("infracost_arch_review_usd", 5000)),
            )
        )
    denies = [f for f in findings if f.severity == "deny"]
    if denies:
        return "FAIL", findings
    if findings:
        return "WARN", findings
    return "PASS", findings
