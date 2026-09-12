# Schema — Data Contracts Between Modules

Lock this before splitting up. Every module reads/writes exactly this shape — no ad hoc fields.

## 1. Parsed JD (Person A → Person B)

```json
{
  "title": "Junior Full Stack Developer Intern",
  "company": "TechNova Solutions",
  "required_skills": ["javascript", "react", "nodejs", "sql"],
  "nice_to_have_skills": ["docker", "aws"],
  "requirement_lines": [
    "Build and maintain REST APIs using Node.js",
    "Develop responsive UI components in React",
    "Collaborate with the team using Git"
  ]
}
```

## 2. Parsed resumes (Person A → Person B)

```json
{
  "resumes": [
    {
      "id": "r01",
      "name": "Candidate Name",
      "raw_text": "...",
      "skills_section": "javascript, express, mongodb, git",
      "experience_bullets": [
        "Built REST APIs with Express and MongoDB",
        "Deployed app on Heroku"
      ],
      "education": "B.Tech Computer Science, 2026"
    }
  ]
}
```

## 3. Ranking output (Person B → Person C)

```json
{
  "rankings": [
    {
      "resume_id": "r01",
      "name": "Candidate Name",
      "final_score": 87.2,
      "keyword_score": 0.80,
      "semantic_score": 0.93,
      "matched_skills": ["javascript", "react", "git"],
      "missing_required": ["sql"],
      "top_evidence": [
        {
          "jd_line": "Build and maintain REST APIs using Node.js",
          "resume_line": "Built REST APIs with Express and MongoDB",
          "similarity": 0.81
        }
      ]
    }
  ]
}
```
Rankings array is sorted descending by `final_score`. All 15–18 resumes appear here, not just
the top 3.

## 4. Explanation output (Person C → demo)

```json
{
  "explanations": [
    {
      "resume_id": "r01",
      "rank": 1,
      "explanation": "Ranked #1 for strong overlap on React and Node.js, with direct experience matching the core JD requirements. Missing: SQL, which the JD lists as required."
    }
  ]
}
```
Only generated for the top 3 `resume_id`s from the ranking output.

## Config file (shared, not per-person)

```json
{
  "fusion_weights": { "alpha_semantic": 0.5, "beta_keyword": 0.5 },
  "fuzzy_match_threshold": 85,
  "required_skill_weight": 2,
  "nice_to_have_weight": 1
}
```
Read by Person B's scoring module. Change values here, not inline in code, so the team can point
to and justify specific numbers during judging.
