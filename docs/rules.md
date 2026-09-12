# Rules — Smart Shortlisting Engine

## Hard constraint from the problem statement
- Do **not** paste a resume and JD into an LLM and ask it to output a score. This will not be
  scored under core criteria, no matter how it's dressed up.
- The keyword and semantic matching must be genuinely implemented in code — real skill
  extraction, real embeddings/similarity, real scoring logic.
- Judges will ask the team to walk through how the matching actually works. Everyone must be
  able to explain the module they built, not just the person who wrote it.
- LLMs are allowed only for **wording** — phrasing an explanation from already-computed facts,
  or the optional bonus chat layer — never for producing the match/score itself.

## Team process rules
- Lock the JSON schema (`scheme.md`) in the first 15 minutes. Do not change field names or
  structure afterward without telling both other people — schema drift is the fastest way to
  lose time on a 5-hour clock.
- Build against mock data first. Nobody waits idle on someone else's module.
- Keep scoring weights and thresholds (α, β, fuzzy-match threshold, taxonomy) in a config file,
  not hardcoded — needed both for tuning and for explaining choices to judges.
- Commit early and often to the shared repo so integration doesn't happen all at once at the end.

## Explanation-generation rule
Top-3 explanations must be built from data that already exists in the ranking output:
matched skills, missing required skills, and the best-matching evidence sentence per JD
requirement. Do not let an LLM invent reasoning that isn't traceable back to computed values.

## Scope discipline
- Core requirement (matching + ranking + top-3 explanations + working demo) always comes before
  bonus features. If time is short, cut bonus, not core.
- Don't over-build the demo UI — it's 15% of the rubric. A clear table of ranked candidates with
  scores and explanations is enough.

## Judging-day rule
Each person should be ready to answer, in their own words:
- What does your module take as input, and what does it output?
- Why did you choose this approach over an alternative?
- What happens on an edge case (e.g. a resume with no matching skills at all)?
