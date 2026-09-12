# Tracker — Hybrid Resume Shortlisting Engine

## Status Legend
- [ ] Not started
- [~] In progress
- [x] Done

---

# Phase 1 — Dataset & Foundation

> The real JD and resume PDFs are runtime inputs supplied later. Until they are
> available, use the synthetic dataset for pipeline development and regression
> checks, without tuning final weights to its categorical labels.

## Shared
- [ ] Inspect the runtime-supplied JD and all provided resumes
- [ ] Identify strong, medium, and weak candidates
- [ ] Identify explicit vs implicit requirements
- [ ] Identify semantic traps and keyword traps
- [ ] Create initial human reference ranking
- [x] Lock shared data schema
- [~] Define scoring configuration and thresholds (initial baseline only)
- [~] Validate PDF extraction quality
- [~] Define golden test cases for matching edge cases
- [x] Add keyword-stuffing adversarial case definition
- [x] Add semantic-without-exact-terminology case definition
- [x] Add ambiguous Node wording case definition
- [x] Add exact-mention-with-weak-evidence case definition
- [x] Add React vs React Native related-skill case definition
- [ ] Define ranking metrics for evaluation

## Person 1 — Data / Parsing
- [~] Implement PyMuPDF extraction
- [~] Implement DOCX extraction
- [ ] Add OCR fallback for poor-quality PDFs
- [ ] Preserve page numbers and section boundaries
- [x] Normalize extracted text
- [x] Detect resume sections for XML and flattened text inputs
- [~] Create candidate evidence store
- [x] Build mixed-format resume manifest

## Person 2 — Matching / Ranking
- [ ] Review JD requirements relevant to scoring
- [ ] Define keyword matching strategy
- [ ] Define semantic matching strategy
- [x] Define requirement-level scoring approach
- [x] Define eligibility vs fit logic
- [x] Prepare mock requirement/evidence data for development

## Person 3 — Evaluation / Demo
- [ ] Design evaluation methodology
- [ ] Define ranking-quality checks
- [ ] Define pairwise comparison checks
- [ ] Design top-3 explanation format
- [ ] Plan Streamlit ranking view
- [ ] Prepare basic demo flow

---

# Phase 2 — JD & Resume Structuring

## Person 1 — Data / Parsing
- [ ] Extract and structure JD requirements
- [ ] Classify required / preferred / nice-to-have
- [ ] Build canonical names
- [ ] Build aliases
- [ ] Attach related skills
- [ ] Define evidence expectations
- [~] Produce `requirements.json` (synthetic fixture created as `mock_requirements.json`)
- [~] Structure all 18 resumes (22 XML/TXT records structured; DOCX/PDF coverage remains)
- [~] Produce `candidates.json` (synthetic candidate fixtures created)

## Person 2 — Matching / Ranking
- [x] Review requirement schema against scoring needs
- [~] Implement canonical skill normalization (initial parser alias map only)
- [~] Prepare matching configuration
- [x] Define mandatory requirement handling
- [x] Define evidence-source and evidence-strength categories
- [x] Define match types: exact / alias / related / semantic

## Person 3 — Evaluation / Demo
- [ ] Inspect structured candidate data
- [ ] Create human reference ranking
- [ ] Identify expected top candidates
- [ ] Document difficult matching cases
- [x] Define explanation output schema

---

# Phase 3 — Core Matching Engine

## Person 1 — Keyword Engine
- [ ] Implement exact matching
- [ ] Implement alias matching
- [ ] Implement controlled fuzzy matching
- [ ] Preserve evidence behind every match
- [ ] Implement BM25 retrieval
- [ ] Produce `keyword_engine.py`

## Person 2 — Semantic + Ranking Engine
- [ ] Load embedding model
- [ ] Embed JD requirements
- [ ] Embed resume evidence chunks
- [ ] Compute cosine similarity
- [ ] Keep strongest semantic evidence per requirement
- [ ] Produce `semantic_engine.py`
- [ ] Implement requirement-level score fusion
- [ ] Implement mandatory requirement eligibility checks and penalties
- [ ] Produce `ranker.py`
- [ ] Cache embeddings and processed artifacts

## Person 3 — Integration / Evaluation
- [ ] Connect parsing output to matching pipeline
- [ ] Run first end-to-end ranking
- [ ] Compare keyword-only vs semantic-only
- [ ] Compare hybrid ranking
- [ ] Evaluate top-k overlap against human reference
- [ ] Evaluate pairwise ranking agreement
- [ ] Identify obvious ranking failures
- [ ] Record failure cases

---

# Phase 4 — Ranking Quality

## Person 1
- [ ] Fix keyword false positives
- [ ] Fix alias problems
- [ ] Test Java vs JavaScript
- [ ] Test React vs React Native
- [ ] Test AWS vs Azure
- [ ] Test fuzzy matching edge cases

## Person 2
- [ ] Tune keyword/semantic fusion
- [ ] Tune requirement weights
- [ ] Tune mandatory penalties
- [ ] Normalize scoring signals
- [ ] Ensure meaningful score spread
- [ ] Validate no score double-counting
- [ ] Generate final rank 1–18

## Person 3
- [ ] Compare ranking against human reference
- [ ] Inspect top candidates
- [ ] Inspect weak candidates
- [ ] Analyze false positives
- [ ] Analyze false negatives
- [ ] Document final scoring behavior

---

# Phase 5 — Explanation Engine

## Person 1
- [ ] Ensure evidence contains source text and provenance
- [ ] Validate evidence references
- [ ] Ensure missing requirements are correctly identified

## Person 2
- [ ] Produce requirement-level match breakdown
- [ ] Produce strongest evidence per requirement
- [ ] Produce matched / weak / missing requirement lists
- [ ] Attach reason codes and confidence values

## Person 3
- [ ] Build top-3 explanation generator
- [ ] Generate strongest matches
- [ ] Generate missing / weak requirements
- [ ] Generate concise candidate summaries
- [ ] Ensure explanations use only verified evidence
- [ ] Produce `explanation.py`

---

# Phase 6 — Reranker (Optional)

## Person 2
- [ ] Retrieve strongest evidence per requirement
- [ ] Test Qwen3-Reranker-0.6B
- [ ] Compare reranked results with baseline
- [ ] Maintain reranker as evidence refinement only
- [ ] Keep reranker only if ranking quality materially improves

## Person 3
- [ ] Evaluate reranker against baseline
- [ ] Document improvement / degradation

## Person 1
- [ ] No dedicated work unless integration requires changes

> If the reranker takes too much time or does not clearly improve results, drop it.

---

# Phase 7 — Streamlit Demo

## Person 3 — Owner
- [ ] Build ranking table
- [ ] Show all 18 candidates
- [ ] Show final score
- [ ] Show keyword score
- [ ] Show semantic score
- [ ] Show mandatory coverage
- [ ] Build candidate detail view
- [ ] Show evidence behind matches
- [ ] Show top-3 explanations
- [ ] Build candidate comparison view

## Person 1
- [ ] Connect extraction/data layer to UI
- [ ] Fix data formatting issues

## Person 2
- [ ] Connect ranking engine to UI
- [ ] Ensure score breakdown is displayed correctly

---

# Phase 8 — Final Validation

## Shared
- [ ] Test malformed PDFs
- [ ] Test missing resume sections
- [ ] Test duplicate skills
- [ ] Test aliases
- [ ] Test Java vs JavaScript
- [ ] Test React vs React Native
- [ ] Test Node.js vs ambiguous "Node" handling
- [ ] Test keyword-heavy weak candidate
- [ ] Test semantic-heavy candidate with few exact keywords
- [ ] Test mandatory requirement failure
- [ ] Test no-evidence case
- [ ] Verify all 18 candidates appear
- [ ] Verify ranking is deterministic
- [ ] Verify top-3 explanations are evidence-grounded
- [ ] Verify keyword and semantic signals both affect final ranking
- [ ] Verify eligibility and fit logic disagree correctly in edge cases

---

# Final Demo Readiness

## Person 1
- [ ] Extraction works end-to-end
- [ ] Resume evidence is correctly displayed
- [ ] No major parsing failures

## Person 2
- [ ] Ranking works end-to-end
- [ ] Keyword + semantic matching demonstrably contribute
- [ ] Mandatory requirements behave correctly
- [ ] Scores are sensible and explainable
- [ ] Scoring configuration is ready to explain to judges

## Person 3
- [ ] Streamlit demo works
- [ ] Top-3 explanations work
- [ ] Candidate comparison works
- [ ] Demo flow rehearsed
- [ ] Judge questions prepared

## Shared
- [ ] Freeze scoring configuration
- [ ] Freeze ranking
- [ ] Freeze explanation format
- [ ] End-to-end test from raw PDFs → final ranking
- [ ] Rehearse judge walkthrough
- [ ] Remove unstable bonus features
