from __future__ import annotations

import re
from dataclasses import dataclass

PROVIDERS = [
    {
        "id": "bedrock-sonnet",
        "name": "Claude Sonnet-tier",
        "via": "AWS Bedrock",
        "q": 0.93,
        "ci": 3.0,
        "co": 15.0,
        "lat": 1.8,
        "priv": True,
        "res": ["US", "EU"],
        "premium": True,
    },
    {
        "id": "bedrock-haiku",
        "name": "Claude Haiku-tier",
        "via": "AWS Bedrock",
        "q": 0.80,
        "ci": 0.8,
        "co": 4.0,
        "lat": 0.6,
        "priv": True,
        "res": ["US", "EU"],
    },
    {
        "id": "azure-gpt",
        "name": "GPT-class",
        "via": "Azure OpenAI",
        "q": 0.91,
        "ci": 2.5,
        "co": 10.0,
        "lat": 1.5,
        "priv": True,
        "res": ["US", "EU"],
    },
    {
        "id": "vertex-flash",
        "name": "Gemini Flash-tier",
        "via": "Vertex AI",
        "q": 0.78,
        "ci": 0.3,
        "co": 2.5,
        "lat": 0.5,
        "priv": True,
        "res": ["US"],
    },
    {
        "id": "hf-llama",
        "name": "Llama 70B (open weights)",
        "via": "HF TGI, self-hosted",
        "q": 0.82,
        "ci": 0.6,
        "co": 0.6,
        "lat": 1.1,
        "priv": True,
        "res": ["US"],
    },
    {
        "id": "anthropic-api",
        "name": "Claude Sonnet-tier",
        "via": "Anthropic API",
        "q": 0.93,
        "ci": 3.0,
        "co": 15.0,
        "lat": 1.6,
        "priv": False,
        "res": ["US"],
    },
    {
        "id": "openai-api",
        "name": "GPT-class",
        "via": "OpenAI API",
        "q": 0.91,
        "ci": 2.5,
        "co": 10.0,
        "lat": 1.4,
        "priv": False,
        "res": ["US"],
    },
]


@dataclass
class RouteRequest:
    prompt: str
    tin: int
    tout: int
    pii: bool
    res: str = "US"
    down: frozenset[str] = frozenset()


def complexity(prompt: str) -> float:
    words = prompt.split()
    c = min(0.5, len(words) / 120)
    if re.search(
        r"compare|analy[sz]e|explain why|step by step|reason|trade-?off|risk|legal|covenant|code|multi",
        prompt,
        re.I,
    ):
        c += 0.35
    if re.search(r"summari[sz]e|classify|extract|yes or no|translate", prompt, re.I):
        c -= 0.15
    return max(0.0, min(1.0, c))


def route(
    req: RouteRequest, weights: dict[str, float] | None = None
) -> dict[str, object]:
    """Pick a catalog row. Never calls a provider."""
    w = weights or {"q": 0.5, "c": 0.35, "l": 0.15}
    c = complexity(req.prompt)
    req_q = 0.72 + 0.2 * c

    def cost(p: dict) -> float:
        return (req.tin * p["ci"] + req.tout * p["co"]) / 1e6

    max_c = max(cost(p) for p in PROVIDERS)
    max_l = max(p["lat"] for p in PROVIDERS)
    rows = []
    for p in PROVIDERS:
        why = ""
        if p["id"] in req.down:
            why = "offline"
        elif p["q"] < req_q:
            why = f"quality {p['q']} < {req_q:.2f} needed"
        elif req.pii and not p["priv"]:
            why = "PII must stay on private endpoint"
        elif req.res not in p["res"]:
            why = f"no {req.res} region"
        score = w["q"] * p["q"] - w["c"] * (cost(p) / max_c) - w["l"] * (p["lat"] / max_l)
        rows.append({**p, "ok": not why, "why": why, "score": score, "cost": cost(p)})
    elig = sorted([r for r in rows if r["ok"]], key=lambda r: r["score"], reverse=True)
    return {
        "pick": elig[0] if elig else None,
        "fallback": elig[1:3],
        "rows": rows,
        "req_q": req_q,
        "complexity": c,
    }
