"""Find actionable cross-band ranking inversions."""

from __future__ import annotations

from itertools import combinations
from typing import Any

from src.evaluation.metrics import BAND_ORDER


def find_failures(
    ranking: list[dict[str, Any]],
    labels: list[dict[str, Any]],
    limit: int = 25,
) -> list[dict[str, Any]]:
    label_by_candidate = {label["candidate_id"]: label["expected_fit"] for label in labels}
    failures = []
    for left, right in combinations(ranking, 2):
        left_band = label_by_candidate.get(left["candidate_id"])
        right_band = label_by_candidate.get(right["candidate_id"])
        if left_band is None or right_band is None or left_band == right_band:
            continue
        if BAND_ORDER[left_band] >= BAND_ORDER[right_band]:
            continue
        failures.append(
            {
                "higher_rank_candidate": summarize(left, left_band),
                "lower_rank_candidate": summarize(right, right_band),
                "reason": f"{left_band} ranked above {right_band}",
            }
        )
        if len(failures) >= limit:
            break
    return failures


def summarize(item: dict[str, Any], band: str) -> dict[str, Any]:
    return {
        "candidate_id": item["candidate_id"],
        "candidate_name": item.get("candidate_name"),
        "band": band,
        "rank": item.get("rank"),
        "final_score": item.get("final_score"),
        "missing_requirements": item.get("missing_requirements", []),
        "top_evidence": [
            result.get("evidence_text", [])[:1]
            for result in item.get("requirement_results", [])
            if result.get("evidence_text")
        ][:3],
    }
