"""Evaluation metrics that respect categorical fit-band labels."""

from __future__ import annotations

from itertools import combinations
from typing import Any


BAND_ORDER = {"weak": 0, "adjacent": 1, "partial": 2, "strong": 3}


def evaluate_ranking(
    ranking: list[dict[str, Any]],
    labels: list[dict[str, Any]],
    top_k: int = 10,
) -> dict[str, Any]:
    label_by_candidate = {label["candidate_id"]: label["expected_fit"] for label in labels}
    ordered = [item for item in ranking if item["candidate_id"] in label_by_candidate]
    pairs = []
    for left, right in combinations(ordered, 2):
        left_band = BAND_ORDER[label_by_candidate[left["candidate_id"]]]
        right_band = BAND_ORDER[label_by_candidate[right["candidate_id"]]]
        if left_band == right_band:
            continue
        expected_before = left_band > right_band
        actual_before = ordered.index(left) < ordered.index(right)
        pairs.append(actual_before == expected_before)

    top_labels = [label_by_candidate[item["candidate_id"]] for item in ordered[:top_k]]
    return {
        "candidate_count": len(ordered),
        "pairwise_comparisons": len(pairs),
        "pairwise_agreement": sum(pairs) / len(pairs) if pairs else 1.0,
        "pairwise_violations": len(pairs) - sum(pairs),
        "top_k": top_k,
        "top_k_band_counts": {band: top_labels.count(band) for band in BAND_ORDER},
        "top_k_strong_count": top_labels.count("strong"),
    }
