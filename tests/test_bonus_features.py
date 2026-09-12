from src.evaluation.jd_bias import flag_jd_bias
from src.explanations.recruiter_chat import answer_why_ranked_above


def test_jd_bias_flags_are_reviewable() -> None:
    findings = flag_jd_bias("We need a young rockstar developer from a top-tier college only")
    assert {finding["category"] for finding in findings} >= {
        "age_or_recency",
        "unnecessary_culture",
        "overly_narrow_background",
    }
    assert all(finding["context"] and finding["phrase"] for finding in findings)


def test_recruiter_answer_uses_mandatory_evidence() -> None:
    higher = {
        "candidate_id": "a",
        "candidate_name": "Candidate A",
        "eligible": True,
        "eligibility": {"mandatory_requirements_missing": []},
        "requirement_results": [],
    }
    lower = {
        "candidate_id": "b",
        "candidate_name": "Candidate B",
        "eligible": False,
        "eligibility": {"mandatory_requirements_missing": ["Node.js"]},
        "requirement_results": [],
    }
    answer = answer_why_ranked_above(higher, lower)
    assert "Candidate A" in answer
    assert "Node.js" in answer