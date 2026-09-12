# Schema — Data Contracts Between Modules

This contract defines the canonical data structures used across parsing, matching, ranking, explanation, and demo layers.

## 1) JD requirement schema

```json
{
  "requirement_id": "req_03",
  "canonical_name": "Node.js",
  "category": "technical_skill",
  "importance": "required",
  "weight": 0.15,
  "aliases": ["nodejs", "node js"],
  "related_skills": ["Express.js", "REST API"],
  "source_text": "Develop backend services using Node.js",
  "evidence_expectations": [
    "direct backend framework experience",
    "REST API implementation",
    "production deployment experience"
  ]
}
```

### JD-level object

```json
{
  "job_title": "Junior Full Stack Developer Intern",
  "company": "TechNova Solutions",
  "requirements": [
    {
      "requirement_id": "req_01",
      "canonical_name": "Node.js",
      "category": "technical_skill",
      "importance": "required",
      "weight": 0.15,
      "aliases": ["nodejs", "node js"],
      "related_skills": ["Express.js", "REST API"],
      "source_text": "Develop backend services using Node.js",
      "evidence_expectations": ["backend services", "REST APIs"]
    }
  ]
}
```

## 2) Resume evidence schema

```json
{
  "candidate_id": "candidate_07",
  "evidence_id": "cand07_exp03",
  "section": "experience",
  "text": "Built REST APIs using Express.js and MongoDB",
  "page": 1,
  "position": 12,
  "extracted_skill": "Express.js",
  "canonical_skill": "Express.js",
  "evidence_type": "project_or_experience",
  "source": "experience",
  "evidence_source_type": "project",
  "evidence_strength": "substantial"
}
```

### Candidate evidence bundle

```json
{
  "candidate_id": "candidate_07",
  "candidate_name": "Candidate 07",
  "evidence": [
    {
      "candidate_id": "candidate_07",
      "evidence_id": "cand07_skill01",
      "section": "skills",
      "text": "JavaScript, Node.js, Express.js, MongoDB",
      "page": 1,
      "position": 2,
      "extracted_skill": "Node.js",
      "canonical_skill": "Node.js",
      "evidence_type": "skill_list",
      "source": "skills",
      "evidence_source_type": "skills_section",
      "evidence_strength": "applied"
    }
  ]
}
```

## 3) Requirement-level match result schema

```json
{
  "candidate_id": "candidate_07",
  "requirement_id": "req_01",
  "canonical_name": "Node.js",
  "importance": "required",
  "match_type": "related",
  "keyword_score": 0.0,
  "semantic_score": 0.76,
  "evidence_strength_score": 0.65,
  "confidence": 0.72,
  "status": "moderate_match",
  "exact_match": false,
  "alias_match": false,
  "fuzzy_match": false,
  "semantic_match": true,
  "reason_codes": ["RELATED_SKILL", "PROJECT_EVIDENCE"],
  "evidence_text": [
    "Built REST APIs using Express.js and MongoDB"
  ],
  "missing": false,
  "notes": "Relevant backend API work indicates strong contextual fit, but the explicit Node.js keyword is absent."
}
```

This ensures a resume can strongly match a requirement semantically without incorrectly claiming an exact literal match.

## 4) Candidate ranking output schema

```json
{
  "rankings": [
    {
      "candidate_id": "candidate_07",
      "candidate_name": "Candidate 07",
      "rank": 1,
      "final_score": 87.4,
      "keyword_score": 0.82,
      "semantic_score": 0.76,
      "mandatory_coverage": 0.92,
      "preferred_coverage": 0.75,
      "missing_requirements": ["SQL"],
      "matched_requirements": ["Node.js", "REST API", "React"],
      "weak_requirements": ["Database design"],
      "top_evidence": [
        {
          "requirement_id": "req_01",
          "canonical_name": "Node.js",
          "resume_text": "Built REST APIs using Express.js and MongoDB",
          "semantic_similarity": 0.81,
          "match_type": "related"
        }
      ]
    }
  ]
}
```

The rankings array is sorted descending by `final_score`, and all 18 candidates should appear in the full output.

## 5) Explanation output schema

```json
{
  "explanations": [
    {
      "candidate_id": "candidate_07",
      "rank": 1,
      "summary": "Strong backend API experience and frontend development overlap with the JD, with only a partial gap on SQL depth.",
      "strongest_matches": [
        "Node.js context via backend API work",
        "React development",
        "MongoDB usage"
      ],
      "missing_or_weak": [
        "SQL depth",
        "AWS familiarity"
      ],
      "evidence_refs": [
        "cand07_exp03",
        "cand07_proj02"
      ],
      "reason_codes": [
        "RELATED_SKILL",
        "PROJECT_EVIDENCE",
        "SEMANTIC_MATCH"
      ]
    }
  ]
}
```

Only the top 3 candidates should receive explanation output in the final demo.

## 6) Shared config schema

```json
{
  "fusion": {
    "keyword_weight": 0.5,
    "semantic_weight": 0.5
  },
  "reranker": {
    "enabled": false,
    "influence": "evidence_refinement"
  },
  "mandatory_penalty": 0.12,
  "fuzzy_match_threshold": 85,
  "required_skill_weight": 2,
  "preferred_skill_weight": 1,
  "nice_to_have_weight": 0.5,
  "embedding_model": "Qwen3-Embedding-0.6B",
  "reranker_model": "Qwen3-Reranker-0.6B"
}
```

The reranker is not added as a separate additive candidate-score component. It refines evidence relevance instead.

These values are the initial development baseline only. They are configurable
and must be evaluated and tuned after the runtime JD and resume set are
inspected. The synthetic mock dataset is for development and regression
testing; it does not define the final scoring weights or candidate order.

## 7) Dataset-level contract

```json
{
  "job_description": {
    "title": "Junior Full Stack Developer Intern",
    "source": "jd.pdf"
  },
  "candidates": [
    {
      "candidate_id": "candidate_01",
      "candidate_name": "Candidate 01",
      "resume_source": "resume_01.pdf"
    }
  ]
}
```

This is the canonical structure used to run the end-to-end evaluation harness
and produce final demo output. The JD and candidate count are runtime inputs;
the hackathon's expected case is one JD with 18 resumes, while development
fixtures may contain a different number of candidates.

## 8) Candidate eligibility and fit contract

```json
{
  "candidate_id": "candidate_07",
  "eligibility": {
    "mandatory_requirements_met": true,
    "mandatory_requirements_missing": ["SQL"],
    "failed_critical_requirements": 1
  },
  "fit": {
    "weighted_requirement_score": 0.85,
    "preferred_requirement_coverage": 0.75
  }
}
```

Eligibility is tracked separately from fit so a candidate who is broadly strong but misses a mandatory requirement cannot outrank a candidate who satisfies the critical requirements.
