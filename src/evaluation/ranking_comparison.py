"""Compare keyword-only, semantic-only, and hybrid ranking modes."""

from __future__ import annotations

from typing import Any


def compare_rankings(*rankings: list[dict[str, Any]], top_k: int = 10) -> dict[str, Any]:
    names = ("keyword", "semantic", "hybrid")
    summary = {}
    for name, ranking in zip(names, rankings):
        summary[name] = {
            "top_candidates": [item["candidate_id"] for item in ranking[:top_k]],
            "eligible_count": sum(item["eligible"] for item in ranking),
            "score_min": min((item["final_score"] for item in ranking), default=0.0),
            "score_max": max((item["final_score"] for item in ranking), default=0.0),
        }
    return summary