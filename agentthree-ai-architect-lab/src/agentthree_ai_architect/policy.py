from __future__ import annotations

import math
import re
from dataclasses import dataclass

STOP = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "of",
    "to",
    "for",
    "in",
    "on",
    "is",
    "are",
    "be",
    "by",
    "with",
    "what",
    "how",
    "do",
    "i",
    "my",
    "me",
    "must",
    "your",
    "can",
    "at",
    "as",
    "it",
    "this",
    "that",
    "from",
    "does",
    "which",
    "need",
    "will",
    "get",
    "any",
    "much",
    "long",
}

CORPUS = [
    {
        "id": "LP-101",
        "title": "Eligibility",
        "text": "Applicants must have a business operating for at least 2 years and annual revenue of at least $100,000. Startups under 2 years are referred to the SBA partner program.",
    },
    {
        "id": "LP-102",
        "title": "Loan amounts",
        "text": "Loan amounts range from $10,000 to $500,000. Any request above $250,000 requires review and sign-off by a human underwriter before a decision is communicated.",
    },
    {
        "id": "LP-103",
        "title": "Cash flow",
        "text": "The debt service coverage ratio DSCR, net operating income divided by annual debt service including the proposed loan, must be at least 1.25.",
    },
    {
        "id": "LP-104",
        "title": "Credit",
        "text": "The minimum business credit score is 650. Scores from 620 to 649 may qualify conditionally with acceptable collateral. Scores below 620 are declined.",
    },
    {
        "id": "LP-105",
        "title": "Documents",
        "text": "Required documents are 2 years of business tax returns and 6 months of business bank statements, plus a government ID for each owner with 20% or more ownership.",
    },
    {
        "id": "LP-106",
        "title": "Fair lending",
        "text": "Decisions must never use protected attributes such as race, religion, sex, national origin, marital status or age. Every decline or conditional decision must state the principal reasons in an adverse action notice under ECOA and Regulation B.",
    },
    {
        "id": "LP-107",
        "title": "Pricing",
        "text": "Rates are set at prime plus 2% to 6% depending on the risk tier assigned by underwriting. Pricing is disclosed before acceptance.",
    },
    {
        "id": "LP-108",
        "title": "Turnaround",
        "text": "A credit decision is delivered within 5 business days after all required documents are received.",
    },
    {
        "id": "LP-109",
        "title": "Data handling",
        "text": "Personal data such as SSNs, emails and phone numbers is redacted before any model call. Decision logs and model inputs are retained for 7 years for audit.",
    },
    {
        "id": "LP-110",
        "title": "Collateral",
        "text": "Accepted collateral includes equipment and commercial real estate. Loan-to-value must not exceed 80% of appraised value.",
    },
]


def stem(word: str) -> str:
    if len(word) > 4:
        return re.sub(r"(ing|ed|es|s)$", "", word)
    return word


def toks(text: str) -> list[str]:
    words = re.sub(r"[^a-z0-9%$]+", " ", text.lower()).split()
    return [stem(w) for w in words if w and w not in STOP]


@dataclass
class Chunk:
    id: str
    title: str
    text: str
    score: float = 0.0


def chunk_docs(size: int = 60, overlap: int = 0) -> list[Chunk]:
    out: list[Chunk] = []
    step = max(1, size - overlap)
    for doc in CORPUS:
        words = doc["text"].split()
        i = 0
        while i < len(words):
            out.append(
                Chunk(
                    id=doc["id"],
                    title=doc["title"],
                    text=" ".join(words[i : i + size]),
                )
            )
            if i + size >= len(words):
                break
            i += step
    return out


def bm25(query: str, chunks: list[Chunk], k: int = 3) -> list[Chunk]:
    docs = [toks(c.title + " " + c.text) for c in chunks]
    n = len(docs)
    avg = sum(len(d) for d in docs) / n
    df: dict[str, int] = {}
    for d in docs:
        for t in set(d):
            df[t] = df.get(t, 0) + 1
    q = toks(query)
    scored: list[Chunk] = []
    for i, chunk in enumerate(chunks):
        d = docs[i]
        tf: dict[str, int] = {}
        for t in d:
            tf[t] = tf.get(t, 0) + 1
        s = 0.0
        for t in q:
            if t not in tf:
                continue
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            s += idf * (tf[t] * 2.5) / (tf[t] + 1.5 * (0.25 + 0.75 * len(d) / avg))
        if s > 0:
            scored.append(
                Chunk(id=chunk.id, title=chunk.title, text=chunk.text, score=s)
            )
    scored.sort(key=lambda c: c.score, reverse=True)
    return scored[:k]


def grounding(answer: str, chunks: list[Chunk]) -> float:
    ctx = set(toks(" ".join(c.text for c in chunks)))
    at = [t for t in toks(re.sub(r"\[LP-\d+\]", "", answer)) if len(t) > 2]
    if not at:
        return 0.0
    return sum(1 for t in at if t in ctx) / len(at)
