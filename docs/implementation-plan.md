# Implementation Plan — Hybrid Resume Shortlisting Engine

## Objective
Build a defensible, evidence-based hybrid ranking engine for one runtime-supplied job description and a runtime-supplied set of resumes. The hackathon's expected evaluation case is one JD and 18 resumes, but the pipeline must not hard-code that count.
The system must rank every candidate, combine keyword and semantic evidence, and explain the top 3 using traceable resume evidence rather than opaque LLM judgments.

## Final recommended architecture

```text
JOB DESCRIPTION
      |
      v
PDF Extraction
PyMuPDF + OCR fallback
      |
      v
JD Requirement Extraction
      |
      +-------------------------------+
      |                               |
      v                               v
Requirement Schema             Skill/Alias Map
      |                               |
      +---------------+---------------+
                      |
                      v
RUNTIME-SUPPLIED RESUMES
      |
      v
PDF Extraction
      |
      v
Resume Section / Evidence Extraction
      |
      v
Candidate Evidence Store
      |
      +--------------------+---------------------+
      |                    |                     |
      v                    v                     v
BM25 lexical retrieval   Keyword matching    Semantic matching
explicit skill signal    exact / alias / fuzzy  embeddings + cosine
      |                    |                     |
      +--------------------+---------------------+
                      |
                      v
Evidence Pool
      |
      +--------------------+---------------------+
      |                                          |
      v                                          v
Optional cross-encoder reranker        Evidence strength
(refine retrieved evidence)            source + strength scoring
      |                                          |
      +--------------------+---------------------+
                           |
                           v
                    Requirement score
                lexical + semantic + strength
                           |
                           v
              Eligibility check + fit scoring
                           |
                           v
                 Weighted candidate ranking
                           |
                           v
                  Top 3 explanations + full table
                           |
                           v
                       React UI served by FastAPI
```

## Core design principle
Do not build:
- JD + resume -> LLM -> score

Build instead:
- documents -> extraction -> structured requirements/evidence -> lexical retrieval -> semantic retrieval -> evidence fusion -> evidence-strength refinement -> requirement-level scoring -> eligibility and fit -> final ranking -> evidence-backed explanation

The ranking engine decides why a candidate ranks where they do. An LLM, if used, only converts verified evidence into clear natural-language output.

## Stage-by-stage breakdown

### 1) Data extraction and normalization
- Extract text from the JD and all resumes using PyMuPDF.
- Use OCR fallback when extraction quality is poor.
- Preserve page numbers and section boundaries.
- Normalize whitespace, bullets, unicode, and common formatting noise.
- Detect resume sections: summary, skills, experience, projects, education, certifications, other.

### 2) JD requirement extraction
Break the JD into individual requirement objects:
- requirement_id
- canonical_name
- category
- importance
- weight
- aliases
- related_skills
- source_text
- evidence_expectations

Separate:
- mandatory/core requirements
- preferred requirements
- nice-to-have requirements

### 3) Resume evidence extraction
Create evidence chunks by meaningful section or bullet instead of one giant resume embedding.
Each evidence item must retain:
- candidate_id
- evidence_id
- section
- text
- page
- position if available
- extracted skill
- canonical skill
- evidence_type
- source

### 4) Keyword matching and BM25
Use a deterministic hierarchy:
1. exact canonical match
2. known alias match
3. controlled fuzzy match
4. semantic relationship

Use BM25 for explicit lexical retrieval per requirement. Store:
- exact_match
- alias_match
- fuzzy_match
- keyword_score

### 5) Semantic matching
For each JD requirement:
- embed the requirement
- embed each candidate evidence chunk
- compute cosine similarity
- keep the strongest semantic evidence
- store semantic score + evidence text

### 6) Evidence fusion and reranking
- Run keyword and semantic matching independently.
- Fuse at requirement level, not at whole-candidate level.
- Initial baseline: 0.5 keyword + 0.5 semantic. This is scaffolding for development, not a final tuned value.
- Optional Qwen3-Reranker-0.6B refines the strongest retrieved evidence only.
- The reranker is not a separate additive term in the candidate score.
- Evidence strength is tracked separately using the source and strength of the underlying evidence.

### 7) Deterministic final scoring
For each requirement:

RequirementScore_i = lexical_component + semantic_component + evidence_strength_component

Then:

CandidateScore = sum(weight_i * RequirementScore_i)

Mandatory penalties and eligibility checks are handled separately so that a candidate missing a critical requirement cannot outrank a candidate who meets it.

The component formula and all initial weights or thresholds are provisional implementation baselines. They must be evaluated against human reference judgments and adversarial cases after the runtime JD and resumes are supplied; they must not be treated as ground-truth labels from the synthetic dataset.

Separate:
1. eligibility / mandatory requirements
2. fit / ranking among viable candidates

### 8) Explanations and demo UI
- Generate structured explanations from matched requirements, evidence, and missing/weak areas.
- Attach reason codes for each requirement result.
- Show ranking, requirement gaps, and evidence for the top 3.
- Build a React UI served by the FastAPI backend with ranking table, candidate detail, and comparison screen.

## Build order (locked)
1. Inspect the runtime-supplied JD and resumes
2. Extract PDFs
3. Structure JD requirements
4. Structure resume evidence
5. Build exact/alias keyword matching
6. Add BM25
7. Add embeddings
8. Build baseline hybrid ranker
9. Evaluate ranking
10. Fix failure cases
11. Add reranker
12. Re-evaluate
13. Build evidence-based explanations
14. Build UI
15. Add one bonus feature only if time remains
16. Stress-test against judge questions
17. Freeze the system

## Team distribution

### Person 1 — ML / matching lead
- JD requirements
- keyword engine
- semantic engine
- scoring and evaluation

### Person 2 — Data / parsing lead
- PDF extraction
- OCR fallback
- section detection
- candidate evidence schema

### Person 3 — Ranking / explanations lead
- reranker (if time permits)
- evidence scoring
- explanation generation
- comparison logic

### Person 4 — UI / integration lead
- React UI served by FastAPI
- API integration
- visualizations and demo flow

## Timeline

### Phase 1 — first 30–45 minutes
- inspect JD
- inspect resumes
- define data schema
- extract PDFs
- validate extraction quality

### Phase 2 — next 45–60 minutes
- extract JD requirements
- structure resume evidence
- build keyword engine
- build basic semantic engine

### Phase 3 — next 30–45 minutes
- baseline hybrid ranking
- rank all 18 candidates
- produce top-3 evidence summaries

### Phase 4 — next 30–45 minutes
- evaluation harness
- inspect ranking failures
- tune requirement weights and alias handling

### Phase 5 — next 30–45 minutes
- add reranker if compute/time allows
- compare against baseline
- keep it only if it improves quality

### Phase 6 — final 45–60 minutes
- React UI served by FastAPI
- explanations
- comparison mode
- end-to-end demo rehearsal

## Risks and mitigations
- Schema drift → lock the contract early and keep all modules aligned.
- Overreliance on LLM score → reject as a core approach; keep LLMs only for explanation phrasing.
- Fuzzy matching treating semantically related but non-equivalent tech as equal → restrict fuzzy matching and keep canonical/alias spacing separate.
- Exact-match inconsistency → only mark exact when the evidence literally contains the canonical skill or accepted alias.
- Double-counting in scoring → use a single requirement-level score with separate mandatory eligibility logic.
- Score clustering → inspect ranking distribution carefully and fix requirement weighting.
- Overbuilding the demo → keep the UI simple and evidence-first; cut bonus features first.

## Decision log to keep in front of the team
- Keyword and semantic matching both matter.
- Related tech is supporting evidence, not automatic equivalence.
- Mandatory requirements should strongly affect ranking.
- Explanations must be grounded in structured evidence.
- The demo should prove the ranking is auditable, not mysterious.
