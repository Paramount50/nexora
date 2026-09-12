# Implementation Plan — Smart Shortlisting Engine

## Architecture (pipeline)

```
Input data (JD + 15-18 resumes, PDF)
        |
Parse and preprocess (extract + segment text)
        |
   -----------------------
   |                     |
Keyword matching     Semantic matching
(taxonomy + fuzzy)   (embeddings + cosine sim)
   |                     |
   -----------------------
        |
Score fusion and ranking (weighted combine, sort)
        |
Top-3 explanations (matched vs missing skills)
```

### Stage details
- **Parse and preprocess**: extract text from JD and resume PDFs (`pdfplumber` / `PyMuPDF`),
  segment resumes into sections (skills, experience, education) via heading/regex detection.
- **Keyword matching**: curated skills taxonomy with alias mapping (`js → javascript`), exact +
  fuzzy match (`rapidfuzz`) against JD's required vs nice-to-have skills.
  `keyword_score = (2*required_matched + 1*nice_to_have_matched) / (2*total_required + 1*total_nice_to_have)`
- **Semantic matching**: sentence-transformer embeddings of JD requirement lines and resume
  bullets, cosine similarity matrix, max-per-JD-line then averaged.
- **Score fusion**: `final_score = α * semantic_score + β * keyword_score`, start at α=β=0.5,
  tune after eyeballing results on the 18 sample resumes. Optional penalty if a hard-required
  skill is fully absent.
- **Explanations**: generated from the already-computed matched/missing skills and top evidence
  sentences. An LLM may be used to phrase this naturally, but not to decide the match itself.

See `scheme.md` for the exact JSON contracts between stages.

## Team distribution (3 people)

### Person A — Data & parsing lead
- PDF extraction for JD + all 18 resumes.
- Section segmentation (skills, experience, education).
- Build the skills taxonomy JSON (terms + aliases).
- Once parsing is stable: builds the demo UI (simple table view of ranked output + score breakdown).

### Person B — Matching & ranking lead
- Keyword matching module (exact + fuzzy, required vs nice-to-have weighting).
- Semantic matching module (embeddings, cosine similarity).
- Score fusion formula and final ranking sort.
- Highest-weighted rubric item (35%) — must be ready to explain the logic and weighting choices
  to judges in detail.

### Person C — Explanation & bonus lead
- Top-3 explanation generator (pulls from Person B's output).
- Optional LLM polish pass on explanation wording.
- Bonus features if time allows: JD bias-flagging, recruiter chat layer.

## Timeline (5-hour build)

| Time | Focus |
|---|---|
| Hour 1 | Lock schema, set up repo, mock data, everyone codes against mocks; Person A starts real parsing |
| Hour 1.5–2.5 | Real integration: parsed output feeds matching modules |
| Hour 2.5–3.5 | Score tuning, explanations built off real ranking output, basic demo view comes together |
| Hour 3.5–4.25 | Bug fixes, run all 18 resumes end-to-end, check ranking spread — cut bonus work now if core isn't solid |
| Hour 4.25–5 | Demo rehearsal — each person walks through their own module |

## First 15–20 minutes (before splitting up)
1. Lock the JSON schema together (`scheme.md`) — do not skip this.
2. Set up the shared repo with `/data`, `/parsing`, `/matching`, `/explanation`, `/demo`.
3. Skim the real `Sample_JD.pdf` and a few real resumes to check actual formatting.
4. Create mock data matching the schema so nobody waits on the real parser.
5. Split and start coding in parallel.

## Risks and mitigations
- **Schema drift between modules** → lock it early, do not modify without telling both other people.
- **Time runs out before bonus features** → bonus is only 10% of the rubric; a clean core beats an
  incomplete system with extras. Cut bonus first.
- **All-similar scores (no spread)** → sanity-check against the 18 resumes, which are deliberately
  varied; if scores cluster, re-check the fusion weights.
- **Can't explain matching logic live** → keep weights/thresholds in a config file, not hardcoded,
  so the team can point to and justify specific numbers.
