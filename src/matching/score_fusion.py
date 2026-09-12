"""Fuse lexical, semantic, and evidence-strength signals per requirement."""

from __future__ import annotations

from typing import Any


DEFAULT_CONFIG = {
    "keyword_weight": 0.5,
    "semantic_weight": 0.5,
    "evidence_strength_weight": 0.15,
}


def fuse_requirement_result(
    keyword_result: dict[str, Any],
    semantic_result: dict[str, Any] | None = None,
    config: dict[str, float] | None = None,
) -> dict[str, Any]:
    settings = {**DEFAULT_CONFIG, **(config or {})}
    keyword_score = clamp(keyword_result.get("keyword_score", 0.0))
    semantic_score = clamp((semantic_result or {}).get("semantic_score", 0.0))
    evidence_strength = clamp(keyword_result.get("evidence_strength_score", 0.0))
    semantic_evidence = semantic_result.get("evidence_text", "") if semantic_result else ""

    weights = (
        settings["keyword_weight"],
        settings["semantic_weight"],
        settings["evidence_strength_weight"],
    )
    total_weight = sum(weights)
    fused_score = (
        settings["keyword_weight"] * keyword_score
        + settings["semantic_weight"] * semantic_score
        + settings["evidence_strength_weight"] * evidence_strength
    ) / total_weight if total_weight else 0.0
    result = {
        **keyword_result,
        "semantic_score": semantic_score,
        "fused_score": clamp(fused_score),
        "semantic_match": semantic_result is not None and semantic_score > 0.0,
        "semantic_evidence_text": [semantic_evidence] if semantic_evidence else [],
    }
    if semantic_result and semantic_result.get("evidence_id"):
        result["semantic_evidence_id"] = semantic_result["evidence_id"]
    return result


def clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
