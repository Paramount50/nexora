"""Deterministic recruiter answers grounded in ranking evidence."""

from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen
from typing import Any


def answer_recruiter_question(
    question: str,
    rankings: list[dict[str, Any]],
) -> str:
    """Answer recruiter questions using only verified ranking evidence."""
    if not rankings:
        return "No analyzed candidates are available yet. Upload a JD and resumes first."

    lowered = question.lower().strip()
    names = {candidate.get("candidate_name", "").lower(): candidate for candidate in rankings}
    mentioned = [candidate for name, candidate in names.items() if name and name in lowered]

    if any(term in lowered for term in ("top", "best", "strongest", "shortlist")):
        return "Top candidates: " + "; ".join(
            f"{candidate['candidate_name']} ({candidate['final_score']:.0f}/100, {candidate['eligibility']['status']})"
            for candidate in rankings[:3]
        ) + "."

    if len(mentioned) >= 2 and any(term in lowered for term in ("why", "above", "versus", "vs", "compare")):
        ordered = sorted(mentioned[:2], key=lambda candidate: candidate.get("rank", 999))
        return answer_why_ranked_above(ordered[0], ordered[1])

    if mentioned and any(term in lowered for term in ("missing", "gap", "risk", "weak")):
        candidate = mentioned[0]
        missing = candidate.get("missing_requirements", [])
        if not missing:
            return f"{candidate['candidate_name']} has no missing requirements in the current analysis."
        return f"{candidate['candidate_name']} has evidence gaps for: {', '.join(missing)}. These are review signals, not claims that the candidate lacks those skills."

    if mentioned:
        candidate = mentioned[0]
        matches = candidate.get("matched_requirements", [])[:5]
        missing = candidate.get("missing_requirements", [])[:3]
        answer = f"{candidate['candidate_name']} ranks #{candidate.get('rank', '?')} with a fit score of {candidate['final_score']:.0f}/100 and status {candidate['eligibility']['status']}."
        if matches:
            answer += f" Strongest covered requirements include {', '.join(matches)}."
        if missing:
            answer += f" Review gaps: {', '.join(missing)}."
        return answer

    return "I can answer shortlist, candidate gap, ranking difference, and evidence questions. Try: 'Why is the top candidate ranked first?'"


def answer_with_gemini(question: str, rankings: list[dict[str, Any]]) -> str | None:
    """Use Gemini only to phrase answers from supplied ranking evidence."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not rankings:
        return None

    evidence_context = [
        {
            "rank": item.get("rank"),
            "candidate": item.get("candidate_name"),
            "score": item.get("final_score"),
            "eligibility": item.get("eligibility"),
            "matched_requirements": item.get("matched_requirements"),
            "missing_requirements": item.get("missing_requirements"),
            "requirement_results": item.get("requirement_results"),
        }
        for item in rankings
    ]
    prompt = (
        "You are Nexora, a recruiter decision-support assistant. Answer the recruiter question "
        "using only the JSON evidence below. Do not invent facts, do not call related skills exact, "
        "and say when evidence is missing. Be concise and mention the relevant candidate or requirements.\n\n"
        f"Question: {question}\n\nEvidence JSON:\n{json.dumps(evidence_context, ensure_ascii=True)}"
    )
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
    request = Request(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return None


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
