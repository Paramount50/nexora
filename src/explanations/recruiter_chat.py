"""Deterministic recruiter answers grounded in ranking evidence."""

from __future__ import annotations

from typing import Any


def answer_why_ranked_above(
    higher: dict[str, Any],
    lower: dict[str, Any],
) -> str:
    higher_results = {item["canonical_name"]: item for item in higher.get("requirement_results", [])}
    lower_results = {item["canonical_name"]: item for item in lower.get("requirement_results", [])}
    advantages = []
    for requirement, higher_result in higher_results.items():
        lower_result = lower_results.get(requirement)
        if lower_result is None:
            continue
        score_delta = higher_result.get("fused_score", 0.0) - lower_result.get("fused_score", 0.0)
        if score_delta > 0.05:
            evidence = higher_result.get("evidence_text", ["no quoted evidence"])[0]
            advantages.append(f"{requirement} ({higher_result['match_type']}): {evidence}")

    if higher.get("eligible") and not lower.get("eligible"):
        missing = ", ".join(lower["eligibility"].get("mandatory_requirements_missing", []))
        return (
            f"{higher.get('candidate_name', higher['candidate_id'])} ranks above "
            f"{lower.get('candidate_name', lower['candidate_id'])} because it satisfies the mandatory requirements. "
            f"The lower-ranked candidate is missing: {missing}."
        )
    if advantages:
        return (
            f"{higher.get('candidate_name', higher['candidate_id'])} ranks above "
            f"{lower.get('candidate_name', lower['candidate_id'])} because it has stronger evidence for "
            + "; ".join(advantages[:3])
            + "."
        )
    return (
        f"{higher.get('candidate_name', higher['candidate_id'])} ranks above "
        f"{lower.get('candidate_name', lower['candidate_id'])} with a higher overall fit score, "
        "but the available requirement-level evidence shows no large individual advantage."
    )
