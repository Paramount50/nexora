"""Candidate eligibility and requirement-weighted ranking."""

from __future__ import annotations

from typing import Any

from src.matching.keyword_matcher import match_requirement
from src.matching.score_fusion import fuse_requirement_result


MANDATORY_MATCH_TYPES = {"exact", "alias", "fuzzy"}
MUST_HAVE_IMPORTANCE = {"required"}
GOOD_TO_HAVE_IMPORTANCE = {"preferred", "nice_to_have"}

MATCH_QUALITY_SCORES = {
    "exact": 1.0,
    "alias": 0.95,
    "fuzzy": 0.80,
    "related": 0.55,
    "none": 0.0,
}


def rank_candidates(
    candidates: list[dict[str, Any]],
    requirements: list[dict[str, Any]],
    semantic_engine: Any | None = None,
    semantic_results: dict[tuple[str, str], dict[str, Any]] | None = None,
    bm25_results: dict[tuple[str, str], dict[str, Any]] | None = None,
    fusion_config: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    rankings = [
        rank_candidate(
            candidate,
            requirements,
            semantic_engine=semantic_engine,
            semantic_results=semantic_results,
            bm25_results=bm25_results,
            fusion_config=fusion_config,
        )
        for candidate in candidates
    ]
    # Candidates who satisfy the JD's must-haves always rank before those who
    # do not. Fit score breaks ties within each eligibility cohort.
    rankings.sort(key=lambda item: (item["eligible"], item["final_score"]), reverse=True)
    for rank, item in enumerate(rankings, start=1):
        item["rank"] = rank
    return rankings


def rank_candidate(
    candidate: dict[str, Any],
    requirements: list[dict[str, Any]],
    semantic_engine: Any | None = None,
    semantic_results: dict[tuple[str, str], dict[str, Any]] | None = None,
    bm25_results: dict[tuple[str, str], dict[str, Any]] | None = None,
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
        bm25_result = (bm25_results or {}).get(
            (candidate["candidate_id"], requirement["requirement_id"])
        )
        requirement_results.append(
            fuse_requirement_result(keyword_result, semantic_result, bm25_result=bm25_result, config=fusion_config)
        )

    required = [item for item in requirement_results if item["importance"] in MUST_HAVE_IMPORTANCE]
    preferred = [item for item in requirement_results if item["importance"] == "preferred"]
    nice_to_have = [item for item in requirement_results if item["importance"] == "nice_to_have"]
    good_to_have = [item for item in requirement_results if item["importance"] in GOOD_TO_HAVE_IMPORTANCE]
    mandatory_missing = [item["canonical_name"] for item in required if not mandatory_met(item)]
    mandatory_coverage = coverage(required, mandatory_met)
    preferred_coverage = coverage(good_to_have, lambda item: not item["missing"])
    nice_to_have_coverage = coverage(nice_to_have, lambda item: not item["missing"])

    # Score in tiers so optional skills cannot drown out the requirements that
    # define the role. Mandatory gaps remain a recruiter-facing risk signal,
    # rather than a hard exclusion from the ranked pool.
    required_score = weighted_requirement_score(required, requirements, requirement_results)
    good_to_have_score = weighted_requirement_score(good_to_have, requirements, requirement_results)
    if required:
        fit_score = 0.90 * required_score + 0.10 * good_to_have_score
    elif good_to_have:
        fit_score = 0.75 * preferred_score + 0.25 * nice_to_have_score
    else:
        fit_score = 0.0

    final_score = round(fit_score * 100, 4)
    meets_mandatory = not mandatory_missing
    eligibility_status = "eligible" if meets_mandatory else "review_required"

    return {
        "candidate_id": candidate["candidate_id"],
        "candidate_name": candidate.get("candidate_name", candidate["candidate_id"]),
        "eligible": meets_mandatory,
        "eligibility": {
            "mandatory_requirements_met": meets_mandatory,
            "meets_mandatory_requirements": meets_mandatory,
            "status": eligibility_status,
            "mandatory_requirements_missing": mandatory_missing,
            "failed_critical_requirements": len(mandatory_missing),
        },
        "fit": {
            "weighted_requirement_score": fit_score,
            "preferred_requirement_coverage": preferred_coverage,
            "good_to_have_coverage": preferred_coverage,
        },
        "final_score": final_score,
        "keyword_score": average(result["keyword_score"] for result in requirement_results),
        "semantic_score": average(result["semantic_score"] for result in requirement_results),
        "bm25_score": average(result.get("bm25_score", 0.0) for result in requirement_results),
        "mandatory_coverage": mandatory_coverage,
        "preferred_coverage": preferred_coverage,
        "good_to_have_coverage": preferred_coverage,
        "nice_to_have_coverage": nice_to_have_coverage,
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


def weighted_requirement_score(
    tier_results: list[dict[str, Any]],
    requirements: list[dict[str, Any]],
    requirement_results: list[dict[str, Any]],
) -> float:
    """Return the evidence score for one importance tier."""
    if not tier_results:
        return 0.0
    weights = {
        result["requirement_id"]: max(
            float(requirement.get("weight", 1.0)), 0.0
        )
        for requirement, result in zip(requirements, requirement_results)
    }
    total_weight = sum(weights.get(result["requirement_id"], 1.0) for result in tier_results)
    if not total_weight:
        return 0.0
    return sum(
        weights.get(result["requirement_id"], 1.0) * requirement_quality_score(result)
        for result in tier_results
    ) / total_weight


def requirement_quality_score(result: dict[str, Any]) -> float:
    """Score evidence quality without requiring a semantic model to be loaded."""
    if result.get("missing"):
        return 0.0
    match_quality = MATCH_QUALITY_SCORES.get(result.get("match_type", "none"), 0.0)
    evidence_strength = max(0.0, min(1.0, float(result.get("evidence_strength_score", 0.0))))
    # A direct skill named in a resume deserves a high base score even when it
    # appears in a compact skills section. Evidence strength differentiates
    # applied work from a list, but should not collapse credible fit scores.
    lexical_quality = 0.90 * match_quality + 0.10 * evidence_strength
    return max(lexical_quality, float(result.get("fused_score", 0.0)))


def average(values: Any) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0
