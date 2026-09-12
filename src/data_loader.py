"""Load and validate the JSON contracts used by the ranking pipeline."""

import json
from pathlib import Path
from typing import Any


class DataContractError(ValueError):
    """Raised when an input JSON document violates the shared contract."""


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise DataContractError(f"Expected a JSON object in {path}")
    return value


def load_dataset(data_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    dataset = load_json(data_dir / "mock_resumes.json")
    requirements = load_json(data_dir / "mock_requirements.json")
    validate_dataset(dataset)
    validate_requirements(requirements)
    return dataset, requirements


def validate_dataset(dataset: dict[str, Any]) -> None:
    candidates = dataset.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise DataContractError("Dataset must contain a non-empty candidates list")

    candidate_ids: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise DataContractError("Each candidate must be an object")
        require_fields(candidate, "candidate", {"candidate_id", "candidate_name", "evidence"})
        candidate_id = candidate["candidate_id"]
        if not isinstance(candidate_id, str) or candidate_id in candidate_ids:
            raise DataContractError(f"Candidate IDs must be unique strings: {candidate_id!r}")
        candidate_ids.add(candidate_id)
        evidence = candidate["evidence"]
        if not isinstance(evidence, list):
            raise DataContractError(f"Evidence must be a list for {candidate_id}")
        for item in evidence:
            if not isinstance(item, dict):
                raise DataContractError(f"Evidence must contain objects for {candidate_id}")
            require_fields(item, "evidence", {"candidate_id", "evidence_id", "text", "section"})
            if item["candidate_id"] != candidate_id:
                raise DataContractError(f"Evidence owner mismatch for {item['evidence_id']}")


def validate_requirements(requirements: dict[str, Any]) -> None:
    items = requirements.get("requirements")
    if not isinstance(items, list) or not items:
        raise DataContractError("Requirements must contain a non-empty requirements list")

    requirement_ids: set[str] = set()
    for requirement in items:
        if not isinstance(requirement, dict):
            raise DataContractError("Each requirement must be an object")
        require_fields(
            requirement,
            "requirement",
            {"requirement_id", "canonical_name", "importance", "weight", "aliases", "related_skills"},
        )
        requirement_id = requirement["requirement_id"]
        if not isinstance(requirement_id, str) or requirement_id in requirement_ids:
            raise DataContractError(f"Requirement IDs must be unique strings: {requirement_id!r}")
        requirement_ids.add(requirement_id)
        if requirement["importance"] not in {"required", "preferred", "nice_to_have"}:
            raise DataContractError(f"Unsupported requirement importance: {requirement['importance']!r}")
        if not isinstance(requirement["weight"], (int, float)) or requirement["weight"] < 0:
            raise DataContractError(f"Requirement weight must be non-negative: {requirement_id}")
        if not isinstance(requirement["aliases"], list) or not isinstance(requirement["related_skills"], list):
            raise DataContractError(f"Aliases and related_skills must be lists: {requirement_id}")


def require_fields(value: dict[str, Any], object_name: str, fields: set[str]) -> None:
    missing = fields.difference(value)
    if missing:
        raise DataContractError(f"{object_name} is missing fields: {sorted(missing)}")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    dataset, requirements = load_dataset(root / "data")
    print(f"Validated {len(dataset['candidates'])} candidates and {len(requirements['requirements'])} requirements")
