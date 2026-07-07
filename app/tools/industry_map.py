from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "industries.json"


def load_industry_knowledge() -> dict[str, Any]:
    return json.loads(DATA_PATH.read_text())


def infer_industry(job_description: str, explicit_industry: str | None = None) -> dict[str, Any]:
    knowledge = load_industry_knowledge()

    if explicit_industry and explicit_industry in knowledge:
        return {
            "matched_industry": explicit_industry,
            "confidence": "explicit",
            "knowledge": knowledge[explicit_industry],
        }

    jd = job_description.lower()
    best_name = "Enterprise SaaS / B2B Software"
    best_score = 0.0

    for industry, info in knowledge.items():
        score = 0.0
        tokens = [industry.lower()]
        tokens += [metric.lower() for metric in info.get("metrics", [])]
        tokens += [role.lower() for role in info.get("roles", [])]
        tokens += [problem.lower() for problem in info.get("business_problems", [])]

        for token in tokens:
            if token and token in jd:
                score += 1.0

        for word in jd.split():
            if len(word) > 6 and word in industry.lower():
                score += 0.5

        if score > best_score:
            best_name = industry
            best_score = score

    return {
        "matched_industry": best_name,
        "confidence": "medium" if best_score > 0 else "fallback",
        "knowledge": knowledge[best_name],
    }
