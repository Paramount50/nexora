"""Hardcoded demo payload for the Junior Full Stack Developer Intern evaluation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_PATH = ROOT / "data" / "mock_requirements.json"

RANKED_CANDIDATES = [
    ("priya_menon", "Priya Menon", 97, True, "fully_eligible"),
    ("divya_krishnan", "Divya Krishnan", 92, True, "fully_eligible"),
    ("aditi_sharma", "Aditi Sharma", 91, True, "fully_eligible"),
    ("farhan_sheikh", "Farhan Sheikh", 90, True, "fully_eligible"),
    ("rohan_verma", "Rohan Verma", 88, True, "fully_eligible"),
    ("nikhil_rao", "Nikhil Rao", 63, True, "fully_eligible"),
    ("meera_pillai", "Meera Pillai", 50, False, "borderline"),
    ("sneha_reddy", "Sneha Reddy", 46, False, "borderline"),
    ("karthik_iyer", "Karthik Iyer", 42, False, "not_eligible"),
    ("pooja_shetty", "Pooja Shetty", 38, False, "not_eligible"),
    ("sanjay_patil", "Sanjay Patil", 36, False, "not_eligible"),
    ("ananya_das", "Ananya Das", 32, False, "not_eligible"),
    ("arjun_kumar", "Arjun Kumar", 22, False, "not_eligible"),
    ("vikram_nair", "Vikram Nair", 18, False, "not_eligible"),
    ("aakash_jain", "Aakash Jain", 16, False, "not_eligible"),
    ("ramya_nagaraj", "Ramya Nagaraj", 12, False, "not_eligible"),
    ("mohammed_faizan", "Mohammed Faizan", 10, False, "not_eligible"),
    ("ishita_gupta", "Ishita Gupta", 5, False, "not_eligible"),
]

SKILL_PROFILES: dict[str, dict[str, str]] = {
    "priya_menon": {
        "JavaScript": "exact", "React": "exact", "Node.js": "exact",
        "SQL": "exact", "Git": "exact", "Docker": "exact", "REST API": "exact",
    },
    "divya_krishnan": {
        "JavaScript": "exact", "React": "exact", "Node.js": "exact",
        "SQL": "related", "Git": "exact", "Docker": "none", "REST API": "exact",
    },
    "aditi_sharma": {
        "JavaScript": "exact", "React": "exact", "Node.js": "exact",
        "SQL": "related", "Git": "exact", "Docker": "none", "REST API": "exact",
    },
    "farhan_sheikh": {
        "JavaScript": "exact", "React": "exact", "Node.js": "exact",
        "SQL": "exact", "Git": "exact", "Docker": "related", "REST API": "exact",
    },
    "rohan_verma": {
        "JavaScript": "exact", "React": "alias", "Node.js": "exact",
        "SQL": "exact", "Git": "exact", "Docker": "none", "REST API": "exact",
    },
    "nikhil_rao": {
        "JavaScript": "exact", "React": "related", "Node.js": "exact",
        "SQL": "related", "Git": "exact", "Docker": "none", "REST API": "exact",
    },
    "meera_pillai": {
        "JavaScript": "exact", "React": "none", "Node.js": "exact",
        "SQL": "exact", "Git": "exact", "Docker": "none", "REST API": "exact",
    },
    "sneha_reddy": {
        "JavaScript": "exact", "React": "exact", "Node.js": "none",
        "SQL": "none", "Git": "exact", "Docker": "none", "REST API": "related",
    },
    "karthik_iyer": {
        "JavaScript": "related", "React": "none", "Node.js": "none",
        "SQL": "exact", "Git": "exact", "Docker": "none", "REST API": "related",
    },
    "pooja_shetty": {
        "JavaScript": "related", "React": "none", "Node.js": "none",
        "SQL": "exact", "Git": "exact", "Docker": "none", "REST API": "related",
    },
    "sanjay_patil": {
        "JavaScript": "fuzzy", "React": "none", "Node.js": "none",
        "SQL": "related", "Git": "exact", "Docker": "none", "REST API": "none",
    },
    "ananya_das": {
        "JavaScript": "related", "React": "none", "Node.js": "none",
        "SQL": "related", "Git": "exact", "Docker": "none", "REST API": "none",
    },
    "arjun_kumar": {
        "JavaScript": "related", "React": "none", "Node.js": "none",
        "SQL": "none", "Git": "exact", "Docker": "none", "REST API": "none",
    },
    "vikram_nair": {
        "JavaScript": "fuzzy", "React": "none", "Node.js": "none",
        "SQL": "related", "Git": "exact", "Docker": "none", "REST API": "none",
    },
    "aakash_jain": {
        "JavaScript": "exact", "React": "none", "Node.js": "none",
        "SQL": "none", "Git": "exact", "Docker": "none", "REST API": "none",
    },
    "ramya_nagaraj": {
        "JavaScript": "fuzzy", "React": "none", "Node.js": "none",
        "SQL": "none", "Git": "related", "Docker": "none", "REST API": "none",
    },
    "mohammed_faizan": {
        "JavaScript": "none", "React": "none", "Node.js": "none",
        "SQL": "none", "Git": "none", "Docker": "none", "REST API": "none",
    },
    "ishita_gupta": {
        "JavaScript": "none", "React": "none", "Node.js": "none",
        "SQL": "none", "Git": "none", "Docker": "none", "REST API": "none",
    },
}

EVIDENCE_SNIPPETS: dict[str, dict[str, str]] = {
    "priya_menon": {
        "React": "Shipped production React features with >80% test coverage across real sprint cycles.",
        "Node.js": "Built Express/Node backends with MongoDB and PostgreSQL in internship and deployed projects.",
        "Docker": "Containerized and deployed full-stack applications with Docker and AWS.",
    },
    "divya_krishnan": {
        "React": "Led a college dev club through agile sprints on a deployed MERN application.",
        "Node.js": "Shipped a MERN stack app with Express REST APIs and CI/CD pipeline.",
        "REST API": "Designed and consumed REST endpoints across frontend and backend layers.",
    },
    "aditi_sharma": {
        "React": "Built React components integrated with existing REST APIs at Zenith Web Labs.",
        "Node.js": "Developed Express services backing internship deliverables in 2-week Jira sprints.",
        "REST API": "Integrated React UI with team REST APIs during internship sprints.",
    },
    "farhan_sheikh": {
        "React": "Full-stack React and Node/Express experience with MongoDB and PostgreSQL.",
    },
    "rohan_verma": {
        "React": "Next.js frontend paired with Node/Express backend — modern framework competency.",
    },
    "nikhil_rao": {
        "React": "Primary frontend experience is Angular rather than React; JD lists React as preferred framing.",
        "Node.js": "Strong Node/Express backend with REST APIs and Git-based team workflow.",
    },
    "meera_pillai": {
        "Node.js": "Strong Node/Express backend delivery, but frontend limited to plain HTML/CSS.",
        "React": "No modern frontend framework experience documented.",
    },
    "sneha_reddy": {
        "React": "Strong React frontend portfolio consuming third-party and Firebase APIs.",
        "Node.js": "No Node.js or custom backend service experience — fails full-stack bar.",
    },
}

TOP_EXPLANATIONS: dict[str, str] = {
    "priya_menon": (
        "Near-complete keyword coverage of both must-haves and good-to-haves: JavaScript, TypeScript, "
        "React, Node.js, Express, MongoDB, PostgreSQL, REST APIs, Git, Docker, AWS, Jest, and explicit "
        "Agile/Scrum experience. Semantically, she's the strongest match — two internships shipping "
        "production features with >80% test coverage plus a deployed, containerized full-stack project."
    ),
    "divya_krishnan": (
        "Strong keyword hit rate: React, Node.js, Express, MongoDB, REST APIs, Git, AWS, Jest, Agile/Scrum. "
        "Led a team through agile sprints and shipped a deployed MERN app with CI/CD — mirrors the JD's "
        "collaborate-in-agile and tested-code requirements. Gap vs #1: experience from college club and "
        "personal projects rather than company internship; no TypeScript or PostgreSQL production use."
    ),
    "aditi_sharma": (
        "Solid must-have coverage: React, Redux, Node.js, Express, MongoDB, REST APIs, Git, plus Jest and "
        "basic AWS. Internship at Zenith Web Labs is the closest real-world analog — React components "
        "integrated with REST APIs in 2-week Jira sprints. Missing vs top two: no TypeScript, no Docker, "
        "no demonstrated cloud deployment of own projects."
    ),
}

ELIGIBILITY_NOTES: dict[str, str] = {
    "priya_menon": "React + Node/Express + MongoDB/PostgreSQL + REST + Git + CS degree",
    "divya_krishnan": "React + Node/Express + MongoDB + REST + Git + CS degree",
    "aditi_sharma": "React + Node/Express + MongoDB + REST + Git + CS degree",
    "farhan_sheikh": "React + Node/Express + MongoDB/PostgreSQL + REST + Git + BCA",
    "rohan_verma": "React/Next.js + Node/Express + PostgreSQL/MongoDB + REST + Git + IT degree",
    "nikhil_rao": "Node/Express + REST + Git + CS degree; frontend is Angular, not React",
    "meera_pillai": "Strong Node/Express backend but no modern frontend framework — HTML/CSS only",
    "sneha_reddy": "Strong React frontend but no Node.js/backend — only Firebase/third-party APIs",
    "karthik_iyer": "Java/Spring backend stack — no React/Angular/Vue or Node.js",
    "pooja_shetty": "PHP/Laravel stack — no React or Node.js",
    "sanjay_patil": "Django/Python backend — no React or Node.js",
    "ananya_das": "Server-rendered stack — missing core web full-stack requirements",
    "arjun_kumar": "Android/mobile focus — no web full-stack evidence",
    "vikram_nair": "ML profile — no web development stack",
    "aakash_jain": "DSA/competitive programming only — no web projects",
    "ramya_nagaraj": "Embedded systems — not aligned with full-stack web role",
    "mohammed_faizan": "Mechanical background with minimal programming",
    "ishita_gupta": "Non-technical business background",
}

METHODOLOGY = {
    "keyword_weight": 60,
    "semantic_weight": 40,
    "keyword_summary": (
        "Direct presence of JD must-haves (JavaScript ES6+, React/modern frontend, Node.js/Express, "
        "REST APIs, SQL/NoSQL, Git) and good-to-haves (TypeScript, cloud, Jest/Mocha, Docker, Agile/Scrum, "
        "live-deployed projects)."
    ),
    "semantic_summary": (
        "Whether experience substance aligns when wording differs — e.g. Angular still signals modern "
        "frontend competency; sprint-based shipping matches agile even without the word 'Agile'. Depth of "
        "full-stack ownership (build, deploy, test both ends) weighted over checklist mentions."
    ),
    "role_summary": (
        "Junior Full Stack Developer Intern — React + Node/Express, REST APIs, SQL/NoSQL, Git, Agile."
    ),
}

ELIGIBILITY_BREAKDOWN = {
    "fully_eligible": [
        {"name": "Priya Menon", "note": ELIGIBILITY_NOTES["priya_menon"]},
        {"name": "Divya Krishnan", "note": ELIGIBILITY_NOTES["divya_krishnan"]},
        {"name": "Aditi Sharma", "note": ELIGIBILITY_NOTES["aditi_sharma"]},
        {"name": "Farhan Sheikh", "note": ELIGIBILITY_NOTES["farhan_sheikh"]},
        {"name": "Rohan Verma", "note": ELIGIBILITY_NOTES["rohan_verma"]},
        {"name": "Nikhil Rao", "note": ELIGIBILITY_NOTES["nikhil_rao"]},
    ],
    "borderline": [
        {"name": "Meera Pillai", "note": ELIGIBILITY_NOTES["meera_pillai"]},
        {"name": "Sneha Reddy", "note": ELIGIBILITY_NOTES["sneha_reddy"]},
    ],
    "not_eligible": [
        {"name": name, "note": ELIGIBILITY_NOTES[cid]}
        for cid, name, *_ in RANKED_CANDIDATES
        if cid in {
            "karthik_iyer", "pooja_shetty", "sanjay_patil", "ananya_das",
            "arjun_kumar", "vikram_nair", "aakash_jain", "ramya_nagaraj",
            "mohammed_faizan", "ishita_gupta",
        }
    ],
}

BOTTOM_LINE = (
    "5 candidates clear the bar cleanly (Priya, Divya, Aditi, Farhan, Rohan). Nikhil is eligible but "
    "off-stack on frontend framework. Two strong specialists (Sneha, Meera) fail the explicit full-stack "
    "requirement — worth a second look if you'd consider training on their missing half."
)


def _load_requirements() -> dict[str, Any]:
    with REQUIREMENTS_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def _requirement_results(candidate_id: str, requirements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    profile = SKILL_PROFILES.get(candidate_id, {})
    snippets = EVIDENCE_SNIPPETS.get(candidate_id, {})
    results = []
    for requirement in requirements:
        name = requirement["canonical_name"]
        match_type = profile.get(name, "none")
        missing = match_type == "none"
        fused = {"exact": 0.95, "alias": 0.85, "related": 0.65, "fuzzy": 0.45, "none": 0.0}[match_type]
        evidence = snippets.get(name)
        if not evidence and not missing:
            evidence = f"Resume shows {match_type} alignment with {name} for this role."
        results.append({
            "requirement_id": requirement["requirement_id"],
            "canonical_name": name,
            "importance": requirement["importance"],
            "category": requirement["category"],
            "match_type": match_type,
            "missing": missing,
            "keyword_score": fused,
            "semantic_score": fused * 0.9 if match_type in {"related", "fuzzy"} else fused,
            "bm25_score": fused * 0.85,
            "fused_score": fused,
            "confidence": fused,
            "evidence_text": [evidence] if evidence else [],
        })
    return results


def _mandatory_coverage(results: list[dict[str, Any]]) -> float:
    required = [item for item in results if item["importance"] == "required"]
    if not required:
        return 1.0
    met = sum(item["match_type"] in {"exact", "alias", "fuzzy"} for item in required)
    return round(met / len(required), 4)


def build_demo_payload() -> dict[str, Any]:
    job = _load_requirements()
    requirements = job["requirements"]
    rankings = []

    for rank, (candidate_id, name, score, eligible, tier) in enumerate(RANKED_CANDIDATES, start=1):
        requirement_results = _requirement_results(candidate_id, requirements)
        mandatory_coverage = _mandatory_coverage(requirement_results)
        missing = [item["canonical_name"] for item in requirement_results if item["missing"]]
        matched = [item["canonical_name"] for item in requirement_results if not item["missing"]]
        explanation = TOP_EXPLANATIONS.get(candidate_id, ELIGIBILITY_NOTES.get(candidate_id, ""))

        rankings.append({
            "candidate_id": candidate_id,
            "candidate_name": name,
            "rank": rank,
            "final_score": float(score),
            "keyword_score": round(score * 0.6, 2),
            "semantic_score": round(score * 0.4, 2),
            "eligible": eligible,
            "eligibility_tier": tier,
            "eligibility_note": ELIGIBILITY_NOTES.get(candidate_id, ""),
            "static_explanation": explanation,
            "mandatory_coverage": mandatory_coverage,
            "preferred_coverage": round(len(matched) / max(len(requirements), 1), 4),
            "missing_requirements": missing,
            "matched_requirements": matched,
            "requirement_results": requirement_results,
            "fit": {"weighted_requirement_score": score / 100},
            "resume_source": "Junior Full Stack Intern pool",
        })

    return {
        "demo_mode": True,
        "job": job,
        "candidate_count": len(rankings),
        "rankings": rankings,
        "methodology": METHODOLOGY,
        "eligibility_breakdown": ELIGIBILITY_BREAKDOWN,
        "bottom_line": BOTTOM_LINE,
        "mode": "hybrid",
        "semantic_enabled": True,
        "scoring_weights": {"keyword": 60, "semantic": 40},
    }
