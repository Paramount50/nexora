# Tracker — Smart Shortlisting Engine

Status legend: `[ ]` not started · `[~]` in progress · `[x]` done

## Setup (all three, first 15–20 min)
- [ ] Lock JSON schema (`scheme.md`) together
- [ ] Set up shared repo: `/data`, `/parsing`, `/matching`, `/explanation`, `/demo`
- [ ] Skim real `Sample_JD.pdf` and a few real resumes
- [ ] Create mock data matching the schema
- [ ] Confirm fusion-weight config file exists and is agreed

## Person A — Data & parsing lead

**Hour 1**
- [ ] PDF extraction working on `Sample_JD.pdf`
- [ ] PDF extraction working on at least 3 real resumes

**Hour 1.5–2.5**
- [ ] Section segmentation (skills / experience / education) for all 18 resumes
- [ ] Skills taxonomy JSON built (terms + aliases)
- [ ] Parsed output matches agreed schema exactly — handed off to Person B

**Hour 2.5–3.5**
- [ ] Start demo UI (Streamlit table: ranked candidates, scores, top-3 explanations)

**Hour 3.5–4.25**
- [ ] Demo UI shows all 18 ranked resumes correctly
- [ ] Handle at least one messy-resume edge case gracefully (bonus, if time allows)

## Person B — Matching & ranking lead

**Hour 1**
- [ ] Keyword matching module runs against mock data
- [ ] Semantic matching module runs against mock data (embeddings loading correctly)

**Hour 1.5–2.5**
- [ ] Keyword + semantic modules running against Person A's real parsed output
- [ ] Score fusion formula implemented, reading weights from config file

**Hour 2.5–3.5**
- [ ] Ranking output produced for all 18 resumes, sorted descending
- [ ] Eyeball the spread — scores should not cluster; tune weights if they do
- [ ] Ranking output matches agreed schema exactly — handed off to Person C

**Hour 3.5–4.25**
- [ ] Can explain, out loud, why the weighting was chosen
- [ ] Edge case checked: resume with zero matching skills doesn't break scoring

## Person C — Explanation & bonus lead

**Hour 1**
- [ ] Explanation generator stubbed against mock ranking output

**Hour 1.5–2.5**
- [ ] Explanation generator pulls real matched/missing skills and evidence from Person B's output

**Hour 2.5–3.5**
- [ ] Top-3 explanations read clearly and are traceable to actual matched/missing data
- [ ] (Optional) LLM polish pass on explanation wording

**Hour 3.5–4.25**
- [ ] Bonus: JD bias-flagging — only if core is fully done
- [ ] Bonus: recruiter chat layer — only if core is fully done and bias-flagging is skipped or done

## Final (Hour 4.25–5, all three)
- [ ] Full run on all 18 resumes end-to-end, no errors
- [ ] Demo rehearsal — each person explains their own module
- [ ] Confirm judging rubric is covered: matching (35%), ranking quality (20%), explanations (20%),
      working demo (15%), bonus (10% — only if time allowed)
