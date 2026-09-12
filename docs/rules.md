# Rules — Hybrid Resume Shortlisting Engine

## Core rule
Do not build the system as:
- JD + resume -> LLM -> score

The authoritative ranking engine must be code-driven: document extraction, requirement extraction, lexical retrieval, semantic retrieval, evidence fusion, requirement-level scoring, and final ranking.

## Hard constraints from the hackathon brief
- Use both keyword matching and semantic matching in the final ranking.
- Keep the keyword and semantic signals separate, not collapsed into a single opaque model call.
- Distinguish direct matches, aliases, related-but-not-equivalent technologies, and semantic matches.
- Treat mandatory requirements as a real gating / penalty mechanism, not just a score boost.
- Only use an LLM for wording or optional Q&A, never for authoritative scoring.

## Match-type rule
Every match must be tagged with a match type:
- exact
- alias
- related
- semantic

Examples:
- Candidate says "Node.js" and JD says "Node.js" => exact
- Candidate says "NodeJS" and JD says "Node.js" => alias
- Candidate says "Express.js" and JD says "Node.js" => related
- Candidate says "Built backend services with a JavaScript runtime" and JD says "Node.js" => semantic

Do not collapse these into a single boolean match state.

## Evidence-first rule
Every important claim about a candidate must come from structured evidence extracted from the resume.
If the resume does not establish a skill or experience claim, the system must record that as no strong evidence found rather than inventing it.

## Negative evidence rule
Do not reduce everything to matched/missing.
We must preserve:
- strong match
- moderate match
- weak/indirect match
- no evidence
- requirement not satisfied
- contradictory evidence where applicable

Examples:
- "3+ years experience" vs "1 year experience" is explicit failure of a requirement, not just missing data.
- "Familiar with React" is not equivalent to "Built and deployed React dashboards."

## Lexical matching rule
Use a deterministic hierarchy:
1. exact canonical match
2. known alias match
3. controlled fuzzy match
4. related evidence
5. semantic relationship

Do not let fuzzy matching decide equivalence by itself.
Dangerous examples include:
- Java vs JavaScript
- React vs React Native
- AWS vs Azure
- Node.js vs unrelated "Node"

Important: never add a blind alias like "node" to a canonical requirement unless context clearly supports it. A bare word like "node" is ambiguous and can create false positives.

## Semantic matching rule
Semantic retrieval must operate per JD requirement against resume evidence chunks, not by embedding the whole JD and whole resume as one giant pair.
Semantic similarity is a supporting and contextual signal. It does not replace explicit skill evidence.

## Score architecture rule
Use one requirement-level score per requirement:

RequirementScore_i = lexical_component + semantic_component + evidence_strength_component

Then:

CandidateScore = sum(weight_i * RequirementScore_i)

Mandatory constraints are applied separately as eligibility checks and penalties, rather than being double-counted inside the same score.

This avoids double counting semantic relevance and evidence strength.

## Eligibility vs fit rule
The system must model two separate ideas:
- Eligibility: whether the candidate satisfies critical requirements
- Fit: how strong the candidate is overall relative to the JD

Example:
- Candidate A has many preferred skills but misses a required skill
- Candidate B meets all required skills but is less broad

Candidate B should rank higher if the mandatory requirement is not satisfied by Candidate A.

## Evidence strength rule
Evidence should be tracked by both source and strength.

Source examples:
- skills section
- coursework
- certification
- project
- internship
- professional experience

Strength examples:
- mention
- exposure
- applied
- substantial
- professional

Example:
- "Python certification" is not equivalent to "Built production Python services in a team."

## Score normalization rule
Before combining signals, normalize keyword, semantic, and reranker scores as needed.
Do not assume raw cosine similarity and keyword coverage are directly comparable without normalization.

## Reranker rule
The reranker is optional and should refine evidence relevance, not be treated as a separate additive candidate score.

The intended flow is:
- lexical evidence + semantic evidence -> retrieved evidence pool
- reranker -> evidence refinement
- requirement score -> final candidate ranking

Do not do: keyword + semantic + reranker as independent additive terms.

## Explanation generation rule
Top-3 explanations must be generated from computed structured evidence:
- matched requirements
- missing or weak requirements
- strongest evidence text
- requirement-level score breakdown
- reason codes

No explanation should claim experience or skills that are not in the evidence pool.

## Reason code rule
Every requirement match should carry reason codes, such as:
- EXACT_KEYWORD
- ALIAS_MATCH
- RELATED_SKILL
- SEMANTIC_MATCH
- PROJECT_EVIDENCE
- PROFESSIONAL_EXPERIENCE
- NO_EVIDENCE

This makes the final explanation layer much easier to defend and debug.

## Process rules
- Lock the schema before implementation starts.
- Build the repo around a shared data contract; no ad hoc fields.
- Keep weights and thresholds in config, not hardcoded into logic.
- Use mock data early to keep everyone productive in parallel.
- Do not reverse the build order.
- Keep bonus features behind the core ranking and explanation pipeline.
- Cache expensive preprocessing and embedding work where possible.

## Scope discipline
- Core ranking and explainability always come before polishing.
- If time gets tight, cut bonus features before weakening the matching engine.
- The UI should be inspectable and evidence-based, not a black-box dashboard.

## Judging-day expectation
Each team member should be able to explain:
- what their module takes as input and produces,
- why the design choice was made,
- how the module behaves on edge cases such as absent skills, indirect matches, or mandatory requirement failures.

## Final rule
The best system is not the one with the most models. It is the one that produces a correct, explainable, defensible ranking of the 18 real resumes with evidence to back it up.
