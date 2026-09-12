# PRD — Smart Shortlisting Engine

## Event
InternLoom AI Hackathon, Manipal Institute of Technology.
8:30 AM inauguration, 4:30 PM prize distribution. Working window: ~5 hours.

## Background
Campus placement platforms rank an entire pool of applicants against one job opening before a
human recruiter looks at them. Candidates rarely describe themselves in the exact words of a JD
(e.g. "built REST APIs with Express and MongoDB" vs a JD that says "Node.js backend"), but
specific tools named in a JD still matter. Resumes also vary widely in structure and completeness.

## Problem statement
Build a system that takes one Job Description and a batch of 15–18 resumes and returns a
ranked, explainable shortlist of candidates.

## Goals
1. Evaluate every resume against the JD using **both** semantic search (meaning-based) and
   keyword search (explicit skills/tools/terms). Both must genuinely factor into the result.
2. Produce a ranked list of all candidates, best fit to worst fit, each with a final score.
3. For the top 3 candidates, generate a short explanation: which skills matched, which required
   skills appear to be missing.

## Hard constraint
Pasting a resume and JD into an LLM and asking for a score out of 100 does **not** meet the
requirement and will not be scored under core criteria. The matching logic must be genuinely
implemented by the team. Judges will ask each team to walk through how the matching actually
works.

## Inputs provided
- `Sample_JD.pdf` — Junior Full Stack Developer Intern role, fictional company TechNova Solutions.
- 18 sample resumes (PDF), deliberately varying in fit — strong, partial, and weak matches — so
  the output should show a meaningful spread, not clustered scores.

## Functional requirements
- Parse JD and resume PDFs into structured text.
- Extract required vs nice-to-have skills from the JD.
- Score every resume on keyword overlap (explicit skills/tools).
- Score every resume on semantic similarity (meaning-based overlap, catches synonyms/adjacent tech).
- Fuse both signals into one final score per resume.
- Rank all candidates by final score.
- Generate a natural-language explanation for the top 3 only, grounded in the actual matched/missing
  skills and evidence — not an invented LLM judgment.

## Bonus (optional, extra points only)
- Flag potential bias or overly narrow phrasing in the JD that could unfairly exclude candidates.
- A UI/chat layer where a recruiter can ask "Why is Candidate X ranked above Candidate Y?" and get
  a natural-language answer.
- Graceful handling of messy/inconsistent resume formatting (typos, varied dates, inconsistent
  section headers).

## Judging rubric
| Criterion | Weight |
|---|---|
| Effective use of both semantic and keyword-based matching | 35% |
| Quality and sensibility of the overall ranking | 20% |
| Accuracy and clarity of top-3 explanations | 20% |
| Working end-to-end demo | 15% |
| Bonus features | 10% |

## Out of scope for a 5-hour build
- Training custom ML models.
- Large-scale resume database / multi-JD support.
- Production-grade auth, storage, or deployment.

## Team
3 people. See `implementation-plan.md` for role split and `tracker.md` for task-level tracking.
