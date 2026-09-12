"""Candidate eligibility and requirement-weighted ranking."""

from __future__ import annotations

from typing import Any

from src.matching.keyword_matcher import match_requirement
from src.matching.score_fusion import fuse_requirement_result


MANDATORY_MATCH_TYPES = {"exact", "alias", "fuzzy"}


def rank_candidates(
    candidates: list[dict[str, Any]],
    requirements: list[dict[str, Any]],
    semantic_engine: Any | None = None,
    semantic_results: dict[tuple[str, str], dict[str, Any]] | None = None,
    fusion_config: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    rankings = [
        rank_candidate(
            candidate,
            requirements,
            semantic_engine=semantic_engine,
            semantic_results=semantic_results,
            fusion_config=fusion_config,
        )
        for candidate in candidates
    ]
    rankings.sort(key=lambda item: (item["eligible"], item["final_score"]), reverse=True)
    for rank, item in enumerate(rankings, start=1):
        item["rank"] = rank
    return rankings


def rank_candidate(
    candidate: dict[str, Any],
    requirements: list[dict[str, Any]],
    semantic_engine: Any | None = None,
    semantic_results: dict[tuple[str, str], dict[str, Any]] | None = None,
    fusion_config: dict[str, float] | None = None,
) -> dict[str, Any]:
    requirement_results = []
    for requirement in requirements:
        keyword_result = match_requirement(requirement, candidate.get("evidence", []))
        semantic_result = (semantic_results or {}).get(
            (candidate["candidate_id"], requirement["requirement_id"])
        )
        if semantic_result is None and semantic_engine is not None and candidate.get("evidence"):
            candidate_semantic_results = semantic_engine.match_requirement(
                requirement, candidate["evidence"], top_k=1
            )
            semantic_result = candidate_semantic_results[0] if candidate_semantic_results else None
            semantic_result = semantic_results[0] if semantic_results else None
        requirement_results.append(
            fuse_requirement_result(keyword_result, semantic_result, config=fusion_config)
        )

    required = [item for item in requirement_results if item["importance"] == "required"]
    preferred = [item for item in requirement_results if item["importance"] == "preferred"]
    mandatory_missing = [item["canonical_name"] for item in required if not mandatory_met(item)]
    mandatory_coverage = coverage(required, mandatory_met)
    preferred_coverage = coverage(preferred, lambda item: not item["missing"])
    total_weight = sum(float(requirement.get("weight", 0.0)) for requirement in requirements)
    weighted_score = sum(
        float(requirement.get("weight", 0.0)) * result["fused_score"]
        for requirement, result in zip(requirements, requirement_results)
    )
    fit_score = weighted_score / total_weight if total_weight else 0.0

    return {
        "candidate_id": candidate["candidate_id"],
        "candidate_name": candidate.get("candidate_name", candidate["candidate_id"]),
        "eligible": not mandatory_missing,
        "eligibility": {
            "mandatory_requirements_met": not mandatory_missing,
            "mandatory_requirements_missing": mandatory_missing,
            "failed_critical_requirements": len(mandatory_missing),
        },
        "fit": {
            "weighted_requirement_score": fit_score,
            "preferred_requirement_coverage": preferred_coverage,
        },
        "final_score": round(fit_score * 100, 4),
        "keyword_score": average(result["keyword_score"] for result in requirement_results),
        "semantic_score": average(result["semantic_score"] for result in requirement_results),
        "mandatory_coverage": mandatory_coverage,
        "preferred_coverage": preferred_coverage,
        "missing_requirements": [result["canonical_name"] for result in requirement_results if result["missing"]],
        "matched_requirements": [result["canonical_name"] for result in requirement_results if not result["missing"]],
        "requirement_results": requirement_results,
    }


def mandatory_met(result: dict[str, Any]) -> bool:
    return result["match_type"] in MANDATORY_MATCH_TYPES


def coverage(results: list[dict[str, Any]], predicate: Any) -> float:
    if not results:
        return 1.0
    return sum(predicate(result) for result in results) / len(results)


def average(values: Any) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0
