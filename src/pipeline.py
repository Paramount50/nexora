"""End-to-end orchestration for the ranking pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.data_loader import load_dataset
from src.matching.bm25_retriever import retrieve_requirement
from src.matching.ranker import rank_candidates
from src.matching.semantic_engine import SemanticEngine


def run_pipeline(
    data_dir: Path,
    semantic_engine: SemanticEngine | None = None,
) -> list[dict[str, Any]]:
    dataset, requirement_data = load_dataset(data_dir)
    candidates = dataset["candidates"]
    requirements = requirement_data["requirements"]
    evidence = [item for candidate in candidates for item in candidate["evidence"]]

    for requirement in requirements:
        retrieve_requirement(requirement, evidence, top_k=5)

    semantic_results = None
    if semantic_engine is not None:
        semantic_results = build_semantic_results(semantic_engine, requirements, evidence)

    return rank_candidates(
        candidates,
        requirements,
        semantic_results=semantic_results,
    )


def build_semantic_results(
    semantic_engine: SemanticEngine,
    requirements: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    results: dict[tuple[str, str], dict[str, Any]] = {}
    for requirement in requirements:
        matches = semantic_engine.match_requirement(requirement, evidence, top_k=len(evidence))
        for match in matches:
            key = (match["candidate_id"], requirement["requirement_id"])
            current = results.get(key)
            if current is None or match["semantic_score"] > current["semantic_score"]:
                results[key] = match
    return results