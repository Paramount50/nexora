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
- [x] Validate PDF extraction quality
- [~] Define golden test cases for matching edge cases
- [x] Add keyword-stuffing adversarial case definition
- [x] Add semantic-without-exact-terminology case definition
- [x] Add ambiguous Node wording case definition
- [x] Add exact-mention-with-weak-evidence case definition
- [x] Add React vs React Native related-skill case definition
- [x] Define ranking metrics for evaluation (band-aware pairwise agreement and top-k composition)

## Person 1 — Data / Parsing
- [x] Implement PyMuPDF extraction
- [x] Implement DOCX extraction
- [~] Add OCR fallback for poor-quality PDFs (implemented; scanned-PDF runtime test pending)
- [x] Preserve page numbers and section boundaries
- [x] Normalize extracted text
- [x] Detect resume sections for XML and flattened text inputs
- [x] Create candidate evidence store
- [x] Build mixed-format resume manifest

## Person 2 — Matching / Ranking
- [ ] Review JD requirements relevant to scoring
- [x] Define keyword matching strategy
- [x] Define semantic matching strategy
- [x] Define requirement-level scoring approach
- [x] Define eligibility vs fit logic
- [x] Prepare mock requirement/evidence data for development

## Person 3 — Evaluation / Demo
- [x] Design evaluation methodology (band-aware synthetic evaluation; human reference remains pending)
- [x] Define ranking-quality checks
- [x] Define pairwise comparison checks
- [x] Identify obvious ranking failures
- [x] Record failure cases
- [x] Design top-3 explanation format
- [x] Plan Streamlit ranking view
- [~] Prepare basic demo flow

---

# Phase 2 — JD & Resume Structuring

## Person 1 — Data / Parsing
- [ ] Extract and structure JD requirements
- [ ] Classify required / preferred / nice-to-have
- [ ] Build canonical names
- [ ] Build aliases
- [ ] Attach related skills
- [ ] Define evidence expectations
- [~] Produce `requirements.json` (synthetic fixture plus deterministic runtime JD extraction)
- [x] Structure dummy resumes across PDF, DOCX, XML, and TXT inputs
- [~] Produce `candidates.json` (synthetic candidate fixtures created; runtime candidate artifact remains)

## Person 2 — Matching / Ranking
- [x] Review requirement schema against scoring needs
- [x] Implement canonical skill normalization
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
- [x] Implement exact matching
- [x] Implement alias matching
- [x] Implement controlled fuzzy matching
- [x] Preserve evidence behind every match
- [x] Implement BM25 retrieval
- [x] Produce `keyword_engine.py`

## Person 2 — Semantic + Ranking Engine
- [x] Load embedding model (`all-MiniLM-L6-v2` fallback validated)
- [x] Embed JD requirements
- [x] Embed resume evidence chunks
- [x] Compute cosine similarity
- [x] Keep strongest semantic evidence per requirement
- [x] Produce `semantic_engine.py` (real fallback model validated; preferred Qwen model remains configurable)
- [x] Implement requirement-level score fusion
- [x] Implement mandatory requirement eligibility checks and penalties
- [x] Produce `ranker.py`
- [x] Cache embeddings and processed artifacts (in-memory baseline)

## Person 3 — Integration / Evaluation
- [x] Connect parsing output to matching pipeline
- [x] Run first end-to-end ranking
- [x] Compare keyword-only vs semantic-only
- [x] Compare hybrid ranking
- [ ] Evaluate top-k overlap against human reference
- [x] Evaluate pairwise ranking agreement against synthetic fit bands
- [x] Identify obvious ranking failures
- [x] Record failure cases

---

# Phase 4 — Ranking Quality

## Person 1
- [~] Fix keyword false positives
- [x] Fix alias problems
- [x] Test Java vs JavaScript
- [x] Test React vs React Native
- [x] Test AWS vs Azure (normalization coverage)
- [x] Test fuzzy matching edge cases

## Person 2
- [ ] Tune keyword/semantic fusion
- [ ] Tune requirement weights
- [ ] Tune mandatory penalties
- [x] Normalize scoring signals
- [x] Ensure meaningful score spread
- [x] Validate no score double-counting
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
- [x] Ensure evidence contains source text and provenance
- [x] Validate evidence references
- [x] Ensure missing requirements are correctly identified

## Person 2
- [x] Produce requirement-level match breakdown
- [x] Produce strongest evidence per requirement
- [x] Produce matched / weak / missing requirement lists
- [x] Attach reason codes and confidence values

## Person 3
- [x] Build top-3 explanation generator
- [x] Generate strongest matches
- [x] Generate missing / weak requirements
- [x] Generate concise candidate summaries
- [x] Ensure explanations use only verified evidence
- [x] Produce `explanation.py`

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
- [x] Build ranking table
- [x] Show all candidates (synthetic demo shows 120; runtime count is configurable)
- [x] Show final score
- [x] Show keyword score
- [x] Show semantic score
- [x] Show mandatory coverage
- [x] Build candidate detail view
- [x] Show evidence behind matches
- [x] Show top-3 explanations
- [x] Build candidate comparison view

## Person 1
- [x] Connect extraction/data layer to UI (runtime JD/resume uploads supported)
- [ ] Fix data formatting issues

## Person 2
- [x] Connect ranking engine to UI
- [x] Ensure score breakdown is displayed correctly

---

# Phase 8 — Final Validation

## Shared
- [x] Run full automated test suite (6 tests passing)
- [x] Test malformed PDFs
- [x] Test missing resume sections
- [x] Test duplicate skills
- [x] Test multi-file runtime upload path
- [x] Test aliases
- [x] Test Java vs JavaScript
- [x] Test React vs React Native
- [x] Test Node.js vs ambiguous "Node" handling
- [x] Test keyword-heavy weak candidate
- [x] Test semantic-heavy candidate with few exact keywords
- [x] Test mandatory requirement failure
- [x] Test no-evidence case
- [ ] Verify all 18 runtime candidates appear
- [x] Verify ranking is deterministic
- [x] Verify top-3 explanations are evidence-grounded
- [x] Verify keyword and semantic signals both affect final ranking
- [x] Verify eligibility and fit logic disagree correctly in edge cases

---

# Final Demo Readiness

## Person 1
- [~] Extraction works end-to-end (dummy PDF/DOCX and runtime upload path validated)
- [x] Resume evidence is correctly displayed
- [x] No major parsing failures in current fixtures

## Person 2
- [x] Ranking works end-to-end on synthetic data
- [x] Keyword + semantic matching demonstrably contribute
- [x] Mandatory requirements behave correctly
- [x] Scores are sensible and explainable on synthetic data
- [~] Scoring configuration is ready to explain to judges (baseline; final tuning pending real data)

## Person 3
- [x] Streamlit demo works (HTTP smoke test passed)
- [x] Top-3 explanations work
- [x] Candidate comparison works
- [~] Demo flow rehearsed
- [ ] Judge questions prepared

## Shared
- [ ] Freeze scoring configuration
- [ ] Freeze ranking
- [ ] Freeze explanation format
- [ ] End-to-end test from raw PDFs → final ranking
- [ ] Rehearse judge walkthrough
- [x] Remove unstable bonus features (reranker remains optional and disabled)
