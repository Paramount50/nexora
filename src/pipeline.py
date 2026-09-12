"""End-to-end orchestration for the ranking pipeline."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from src.data_loader import load_dataset, load_runtime_dataset
from src.evaluation.jd_bias import flag_jd_bias
from src.matching.bm25_retriever import retrieve_requirement
from src.matching.ranker import rank_candidates
from src.matching.semantic_engine import SemanticEngine
from src.parsing.jd_loader import extract_jd_text, extract_requirements
from src.parsing.resume_loader import load_resume


def run_pipeline(
    data_dir: Path,
    semantic_engine: SemanticEngine | None = None,
    fusion_config: dict[str, float] | None = None,
    prefer_runtime: bool = True,
) -> list[dict[str, Any]]:
    if prefer_runtime:
        dataset, requirement_data = load_runtime_dataset(data_dir)
    else:
        dataset, requirement_data = load_dataset(data_dir)
    return rank_documents(
        dataset["candidates"],
        requirement_data["requirements"],
        semantic_engine=semantic_engine,
        fusion_config=fusion_config,
    )


def rank_documents(
    candidates: list[dict[str, Any]],
    requirements: list[dict[str, Any]],
    semantic_engine: SemanticEngine | None = None,
    fusion_config: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    evidence = [item for candidate in candidates for item in candidate.get("evidence", [])]
    bm25_results = build_bm25_results(requirements, evidence)

    semantic_results = None
    if semantic_engine is not None:
        semantic_results = build_semantic_results(semantic_engine, requirements, evidence)

    return rank_candidates(
        candidates,
        requirements,
        semantic_results=semantic_results,
        bm25_results=bm25_results,
        fusion_config=fusion_config,
    )


def build_bm25_results(
    requirements: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    results: dict[tuple[str, str], dict[str, Any]] = {}
    if not evidence:
        return results
    for requirement in requirements:
        matches = retrieve_requirement(requirement, evidence, top_k=len(evidence))
        for match in matches:
            cid = match.get("candidate_id")
            if not cid:
                continue
            key = (cid, requirement["requirement_id"])
            current = results.get(key)
            if current is None or match["normalized_score"] > current["normalized_score"]:
                results[key] = match
    return results


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


def rank_uploaded_inputs(jd_upload, resume_uploads, semantic_engine=None, fusion_config=None):
    """Rank candidates from runtime-uploaded JD and resume file objects."""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        jd_path = root / jd_upload.name
        jd_path.write_bytes(jd_upload.getvalue())
        jd_text = extract_jd_text(jd_path)
        requirements = extract_requirements(jd_text)["requirements"]
        candidates = []
        for upload in resume_uploads:
            path = root / upload.name
            path.write_bytes(upload.getvalue())
            candidates.append(load_resume(path))
        rankings = rank_documents(
            candidates,
            requirements,
            semantic_engine=semantic_engine,
            fusion_config=fusion_config,
        )
        return rankings, flag_jd_bias(jd_text)