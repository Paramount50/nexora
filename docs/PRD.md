# PRD — InternLoom AI Hackathon Resume Matching Engine

## Event
InternLoom AI Hackathon — smart shortlisting engine for one JD and 18 resumes.

## Background
Recruiters must compare a single job description against a batch of applicants quickly and defensibly. The challenge is not just finding obvious keyword overlap; it is ranking candidates based on both explicit skills and contextual signals while preserving explainability.

The improved plan treats the problem as evidence-first retrieval and scoring, not as an LLM-only black-box evaluator. The ranking engine must inspect structured evidence, weigh mandatory requirements appropriately, and explain the top candidates using actual match evidence from the resumes.

## Problem statement
Build a system that:
1. evaluates every resume against the JD,
2. genuinely uses both keyword matching and semantic matching,
3. ranks all 18 candidates from best to worst,
4. produces a final score for every candidate,
5. generates clear, evidence-backed explanations for the top 3,
6. runs reliably enough for a live hackathon demo.

## Goals
- Use lexical matching, semantic matching, and requirement-level evidence in the same scoring pipeline.
- Recognize explicit matches and contextual matches without treating related technologies as exact equivalence.
- Capture negative and missing evidence, especially for mandatory requirements.
- Produce rankings that are explainable under judge scrutiny.

## Non-negotiable constraints
- Do not make an LLM the authoritative ranking engine.
- Do not paste JD + resume into an LLM and ask for a score.
- The system must keep keyword and semantic signals separate and auditable.
- Every major claim must be traceable to structured evidence extracted from the resume.

## Inputs provided
- One job description PDF
- 18 resume PDFs
- A real-world challenge dataset with varying candidate quality and inconsistent formatting

## Functional requirements
- Extract text from the JD and resumes with PyMuPDF and OCR fallback as needed.
- Parse the JD into requirement objects with aliases, importance, and related skills.
- Parse each resume into structured section evidence with provenance.
- Run exact, alias, fuzzy, and BM25-based lexical matching.
- Run semantic matching using embeddings per JD requirement vs resume evidence chunks.
- Fuse lexical and semantic signals into a requirement-level candidate score.
- Add mandatory requirement penalties and evidence-strength weighting.
- Rank all candidates after scoring.
- Produce top-3 evidence-backed explanations.
- Provide an inspectable demo view for ranking and candidate comparisons.

## Ranked output requirements
The final system must return:
- rank for all candidates
- final score for all candidates
- keyword score
- semantic score
- reranker score if used
- mandatory coverage
- preferred coverage
- missing requirements
- evidence strength

## Explanation requirements
For the top 3 candidates, show:
- strongest matched skills
- evidence for important requirements
- missing or weak requirements
- concise comparison to the role

The explanation cannot invent unsupported experience or skills.

## Bonus features
Optional only if core ranking is stable:
- JD bias / overly narrow wording detector
- recruiter Q&A for comparing candidates
- messy resume handling for inconsistent formatting

## Judging rubric
| Criterion | Weight |
|---|---:|
| Hybrid semantic + keyword matching | 35% |
| Ranking quality | 20% |
| Top-3 explanations | 20% |
| Working end-to-end demo | 15% |
| Bonus features | 10% |

## Out of scope
- Training custom ML models from scratch
- Large-scale ATS infrastructure
- Elasticsearch or vector databases for this small hackathon dataset
- Kubernetes or microservice-heavy architecture
- Unnecessary production authentication or deployment work

## Success definition
The project is successful if the team can defend the ranking with real evidence, explain why a candidate is higher or lower than another, and show a working end-to-end system under time pressure without relying on a black-box LLM score.

## Team and references
- implementation-plan.md: architecture, phases, and execution order
- scheme.md: data contracts
- rules.md: hard constraints and process discipline
- tracker.md: task tracking
