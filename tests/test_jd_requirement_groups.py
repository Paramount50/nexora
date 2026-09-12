from src.matching.keyword_matcher import match_requirement
from src.matching.ranker import rank_candidate
from src.parsing.jd_loader import extract_requirements


def test_jd_alternatives_become_single_must_have_groups() -> None:
    jd = """
    Junior Full Stack Developer

    Must-have skills
    - JavaScript (ES6+) and at least one modern frontend framework (React preferred)
    - Experience building backend services with Node.js and Express (or similar)
    - Working knowledge of REST APIs and JSON
    - Familiarity with SQL or NoSQL databases (MySQL, PostgreSQL, MongoDB)
    - Version control experience with Git/GitHub
    - Pursuing or holding a degree in Computer Science, IT, or a related field

    Good-to-have skills
    - TypeScript
    - Cloud basics (AWS/GCP/Azure)
    - Testing frameworks (Jest, Mocha)
    """

    requirements = extract_requirements(jd)["requirements"]
    names = {requirement["canonical_name"] for requirement in requirements}

    assert "Modern frontend framework" in names
    assert "SQL or NoSQL database" in names
    assert "Git version control" in names
    assert "CS/IT-related degree" in names
    assert "PostgreSQL" not in names
    assert "MongoDB" not in names
    assert "GitHub" not in names


def test_explicitly_negated_frontend_skills_do_not_pass_must_have() -> None:
    requirement = {
        "requirement_id": "frontend",
        "canonical_name": "Modern frontend framework",
        "importance": "required",
        "acceptable_skills": ["React", "Angular", "Vue.js"],
        "related_skills": [],
    }
    evidence = [
        {
            "candidate_id": "backend_only",
            "evidence_id": "summary_1",
            "section": "summary",
            "text": "Backend developer with Node.js experience. Has not worked with",
            "evidence_strength": "mentioned",
        },
        {
            "candidate_id": "backend_only",
            "evidence_id": "summary_2",
            "section": "summary",
            "text": "React, Angular, or Vue on the frontend.",
            "evidence_strength": "mentioned",
        },
    ]

    result = match_requirement(requirement, evidence)
    assert result["missing"] is True


def test_eligibility_requires_all_must_haves_not_a_score_threshold() -> None:
    requirements = [
        {
            "requirement_id": "node",
            "canonical_name": "Node.js",
            "importance": "required",
            "weight": 2.0,
            "related_skills": [],
        },
        {
            "requirement_id": "react",
            "canonical_name": "React",
            "importance": "required",
            "weight": 2.0,
            "related_skills": [],
        },
    ]
    candidate = {
        "candidate_id": "backend_only",
        "candidate_name": "Backend Only",
        "evidence": [
            {
                "candidate_id": "backend_only",
                "evidence_id": "project_1",
                "section": "projects",
                "text": "Built a Node.js REST service with MongoDB.",
                "evidence_strength": "substantial",
            }
        ],
    }

    result = rank_candidate(candidate, requirements)
    assert result["eligible"] is False
    assert result["eligibility"]["mandatory_requirements_missing"] == ["React"]
