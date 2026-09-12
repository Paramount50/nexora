import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { AnimatePresence, motion } from 'framer-motion';
import './styles.css';
import './dark.css';

const importanceLabel = (importance) => importance === 'required' ? 'Must-have' : importance === 'nice_to_have' ? 'Bonus' : 'Good-to-have';
const matchLabel = { exact: 'Exact', alias: 'Alias', related: 'Related', fuzzy: 'Inferred', none: 'Missing' };
const tierLabel = { fully_eligible: 'Fully eligible', borderline: 'Borderline', not_eligible: 'Not eligible' };

function toCandidate(item) {
  const results = item.requirement_results || [];
  const firstEvidence = results.find(result => result.evidence_text?.length)?.evidence_text?.[0];
  return {
    ...item,
    id: item.candidate_id,
    name: item.candidate_name || item.candidate_id,
    initials: (item.candidate_name || item.candidate_id).split(/\s+/).map(part => part[0]).join('').slice(0, 2).toUpperCase(),
    score: Math.round(item.final_score || 0),
    keywordScore: Math.round(item.keyword_score || 0),
    semanticScore: Math.round(item.semantic_score || 0),
    role: item.resume_source || 'Candidate pool',
    summary: item.static_explanation || `Fit score ${Math.round(item.final_score || 0)} with ${Math.round((item.mandatory_coverage || 0) * 100)}% must-have coverage.`,
    risk: item.eligibility_note || (item.missing_requirements?.length ? item.missing_requirements.join(', ') : 'No critical gaps noted'),
    matches: results.map(result => [result.canonical_name, result.match_type]),
    evidence: firstEvidence || 'No supporting resume evidence was found for this requirement.',
  };
}

function Chip({ type, children }) { return <span className={`chip chip-${type}`}>{children || matchLabel[type] || type}</span>; }
function Icon({ children }) { return <span className="icon" aria-hidden="true">{children}</span>; }
function EvidenceSignal({ children, type = 'exact' }) { return <span className={`evidence-signal signal-${type}`}>{children}</span>; }
function evidenceStrength(type) { return type === 'exact' || type === 'alias' ? 'Strong evidence' : type === 'related' ? 'Related evidence' : type === 'fuzzy' ? 'Inferred evidence' : 'No evidence'; }
function evidenceSignals(candidate) {
  return (candidate.requirement_results || []).filter(result => result.evidence_text?.length).slice(0, 2).map(result => [
    result.importance === 'required' ? 'Must-have' : 'Good-to-have',
    result.canonical_name,
    result.match_type,
  ]);
}
function CoverageLegend({ requirements }) {
  const mustHave = requirements.filter(requirement => requirement.importance === 'required').length;
  const goodToHave = requirements.length - mustHave;
  return <div className="coverage-legend">
    <span className="legend-label">{mustHave} must-have · {goodToHave} good-to-have · 60% keyword · 40% semantic</span>
    <span><i className="legend-swatch exact" />Exact / alias</span><span><i className="legend-swatch related" />Related</span><span><i className="legend-swatch semantic" />Inferred</span><span><i className="legend-swatch missing" />Missing</span>
  </div>;
}
function exportBrief(candidates, jobTitle) {
  const lines = ['NEXORA SHORTLIST', jobTitle, '', 'Methodology: 60% keyword + 40% semantic', '', 'Top candidates'];
  candidates.slice(0, 3).forEach(candidate => {
    lines.push(`#${candidate.rank} ${candidate.name} — ${candidate.score}/100 — ${candidate.eligible ? 'Eligible' : 'Needs review'}`);
    lines.push(candidate.summary);
    lines.push(`Note: ${candidate.risk}`);
    lines.push('');
  });
  const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'nexora-shortlist.txt';
  link.click();
  URL.revokeObjectURL(url);
}

function App() {
  const [screen, setScreen] = useState('ranking');
  const [analysis, setAnalysis] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [compareIds, setCompareIds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const candidates = useMemo(() => (analysis?.rankings || []).map(toCandidate), [analysis]);
  const requirements = analysis?.job?.requirements || [];
  const selected = candidates.find(candidate => candidate.id === selectedId) || candidates[0];
  const go = (next) => setScreen(next);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch('/api/demo')
      .then(response => response.json())
      .then(payload => {
        if (cancelled) return;
        setAnalysis(payload);
        const normalized = (payload.rankings || []).map(toCandidate);
        setSelectedId(normalized[0]?.id || null);
        setCompareIds(normalized.slice(0, 2).map(candidate => candidate.id));
        setScreen('ranking');
      })
      .catch(() => {
        if (!cancelled) setError('Could not load demo results. Is the FastAPI backend running on port 8000?');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return <div className="app-shell"><main className="main-content"><div className="workspace"><p className="section-kicker">NEXORA / LOADING</p><h2>Loading pre-computed ranking…</h2></div></main></div>;
  }

  return <div className="app-shell"><main className="main-content">
    <header className="topbar"><div className="topbar-brand"><div className="brand-mark">N</div><div><p className="eyebrow">NEXORA / DEMO RESULTS</p><h1>{analysis?.job?.job_title || 'Junior Full Stack Developer Intern'}</h1></div></div>
      {analysis && <nav className="top-nav">
        <button className={screen === 'ranking' || screen === 'detail' || screen === 'compare' ? 'nav-link active' : 'nav-link'} onClick={() => go('ranking')}>Ranking</button>
        <button className={screen === 'shortlist' ? 'nav-link active' : 'nav-link'} onClick={() => go('shortlist')}>Top 3</button>
        <button className={screen === 'methodology' ? 'nav-link active' : 'nav-link'} onClick={() => go('methodology')}>Methodology</button>
        <button className={screen === 'eligibility' ? 'nav-link active' : 'nav-link'} onClick={() => go('eligibility')}>Eligibility</button>
      </nav>}
      <div className="top-actions">{analysis && <><span className="live-dot">●</span><span>{analysis.candidate_count} candidates · 60/40 hybrid</span></>}</div>
    </header>
    {error && <div className="error-banner">{error}</div>}
    <AnimatePresence mode="wait">
      {screen === 'ranking' && analysis && <RankingScreen key="ranking" {...{ candidates, requirements, selectedId, setSelectedId, go, analysis }} />}
      {screen === 'detail' && selected && <DetailScreen key="detail" candidate={selected} requirements={requirements} go={go} />}
      {screen === 'compare' && analysis && <CompareScreen key="compare" go={go} candidates={candidates} requirements={requirements} compareIds={compareIds} setCompareIds={setCompareIds} />}
      {screen === 'shortlist' && analysis && <ShortlistScreen key="shortlist" go={go} candidates={candidates} jobTitle={analysis.job?.job_title} setSelectedId={setSelectedId} />}
      {screen === 'methodology' && analysis && <MethodologyScreen key="methodology" analysis={analysis} go={go} />}
      {screen === 'eligibility' && analysis && <EligibilityScreen key="eligibility" analysis={analysis} go={go} />}
    </AnimatePresence>
  </main></div>;
}

function RankingScreen({ candidates, requirements, selectedId, setSelectedId, go, analysis }) {
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('All candidates');
  const filtered = candidates.filter(candidate => candidate.name.toLowerCase().includes(query.toLowerCase()) && (
    filter === 'All candidates' ||
    (filter === 'Eligible' ? candidate.eligible : !candidate.eligible)
  ));
  const eligibleCount = candidates.filter(candidate => candidate.eligible).length;
  const mustHaveCount = requirements.filter(requirement => requirement.importance === 'required').length;
  const weights = analysis?.scoring_weights || { keyword: 60, semantic: 40 };

  return <motion.div className="workspace" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
    <section className="hero-line"><div><p className="section-kicker">RANKED LIST / {candidates.length} CANDIDATES</p><h2>Hybrid evaluation results</h2><p className="muted">{analysis?.methodology?.role_summary || 'Pre-computed ranking for the Junior Full Stack Developer Intern role.'}</p></div><div className="hero-stats"><div><strong>{eligibleCount}</strong><span>eligible</span></div><div><strong>{weights.keyword}/{weights.semantic}</strong><span>keyword/semantic</span></div><div><strong>{candidates[0]?.score || 0}</strong><span>top score</span></div></div></section>
    <div className="control-row"><div className="search"><Icon>⌕</Icon><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Search candidates" /></div><select value={filter} onChange={event => setFilter(event.target.value)}><option>All candidates</option><option>Eligible</option><option>Needs review</option></select><button className="outline-button" onClick={() => go('compare')}>Compare candidates <span>↗</span></button><button className="dark-button" onClick={() => go('shortlist')}>View top 3</button></div><CoverageLegend requirements={requirements} />
    <div className="table-wrap"><div className="table-head"><span>Rank / candidate</span><span>Eligibility</span><span>Score /100</span><span>KW / SEM</span><span>Coverage</span><span> </span></div>{filtered.map((candidate, index) => <motion.button key={candidate.id} className={`candidate-row ${index === 0 ? 'top-row' : ''} ${selectedId === candidate.id ? 'selected' : ''}`} onClick={() => { setSelectedId(candidate.id); go('detail'); }} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.05 }}><div className="candidate-cell"><span className="rank-number">{String(candidate.rank).padStart(2, '0')}</span><span className="person-avatar">{candidate.initials}</span><span><strong>{candidate.name}</strong><small>{tierLabel[candidate.eligibility_tier] || candidate.role}</small></span></div><div><span className={`eligibility ${candidate.eligible ? 'good' : 'bad'}`}>{candidate.eligible ? 'Eligible' : candidate.eligibility_tier === 'borderline' ? 'Borderline' : 'Not eligible'}</span></div><div className="score">{candidate.score}</div><div className="coverage"><small className="mono">{candidate.keywordScore} / {candidate.semanticScore}</small><div className="segmented">{requirements.map(requirement => { const result = candidate.requirement_results?.find(item => item.canonical_name === requirement.canonical_name); return <i key={requirement.requirement_id} className={`segment ${result?.match_type || 'none'}`} title={`${requirement.canonical_name}: ${importanceLabel(requirement.importance)} / ${result?.match_type || 'missing'}`} />; })}</div></div><div className="row-signals">{evidenceSignals(candidate).map(([source, skill, type]) => <EvidenceSignal key={`${source}-${skill}`} type={type}>{source} · {skill}</EvidenceSignal>)}</div><span className="row-arrow">→</span></motion.button>)}</div>
    <div className="table-footer"><span>Showing {filtered.length} of {candidates.length} candidates</span><button className="text-button view-all" onClick={() => { setQuery(''); setFilter('All candidates'); }}>View all →</button><span><b>Scoring:</b> {weights.keyword}% keyword + {weights.semantic}% semantic</span></div>
  </motion.div>;
}

function DetailScreen({ candidate: c, requirements, go }) {
  const [req, setReq] = useState(requirements[0]?.canonical_name || '');
  const selectedResult = c.requirement_results?.find(result => result.canonical_name === req) || c.requirement_results?.[0];
  return <motion.div className="workspace" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }}><button className="back-link" onClick={() => go('ranking')}>← Back to ranking</button><section className="detail-header"><div><p className="section-kicker">CANDIDATE / {String(c.rank).padStart(2, '0')}</p><h2>{c.name}</h2><p className="muted">{c.risk}</p></div><div className="detail-score"><span>SCORE /100</span><strong>{c.score}</strong><span className={`eligibility ${c.eligible ? 'good' : 'bad'}`}>{tierLabel[c.eligibility_tier] || (c.eligible ? 'Eligible' : 'Not eligible')}</span></div></section>
    {c.static_explanation && <div className="why-box"><span className="section-kicker">EVALUATION SUMMARY</span><p>{c.static_explanation}</p></div>}
    <div className="detail-grid"><section className="evidence-list"><div className="panel-heading"><span>Requirement breakdown</span><span className="muted">KW {c.keywordScore} · SEM {c.semanticScore}</span></div>{requirements.map(requirement => { const result = c.requirement_results?.find(item => item.canonical_name === requirement.canonical_name) || { match_type: 'none', missing: true }; return <button className={`requirement-row ${req === requirement.canonical_name ? 'active' : ''}`} key={requirement.requirement_id} onClick={() => setReq(requirement.canonical_name)}><span><strong>{requirement.canonical_name}</strong><small>{importanceLabel(requirement.importance)} · {requirement.category}</small></span><span className="strength-label">{evidenceStrength(result.match_type)}</span><Chip type={result.match_type} /></button>; })}</section><section className="excerpt-panel"><div className="panel-heading"><span>Evidence excerpt</span><span className="source-tag">{selectedResult?.importance === 'required' ? 'MUST-HAVE' : 'GOOD-TO-HAVE'}</span></div><div className="excerpt-meta"><span className="mono">MATCHED EVIDENCE / {req.toUpperCase()}</span><span className="confidence">Confidence {selectedResult ? Number(selectedResult.confidence || selectedResult.fused_score || 0).toFixed(2) : '0.00'}</span></div><p className="excerpt">{selectedResult?.evidence_text?.[0] || 'No supporting evidence found in this resume.'}</p></section></div></motion.div>;
}

function CompareScreen({ go, candidates, requirements, compareIds, setCompareIds }) {
  const a = candidates.find(candidate => candidate.id === compareIds[0]) || candidates[0];
  const b = candidates.find(candidate => candidate.id === compareIds[1]) || candidates[1] || candidates[0];
  const updateCandidate = (side, id) => setCompareIds(current => side === 0 ? [id, current[1]] : [current[0], id]);
  const matchFor = (candidate, requirement) => candidate?.requirement_results?.find(result => result.canonical_name === requirement.canonical_name) || { match_type: 'none' };
  if (!a || !b) return null;
  return <motion.div className="workspace" initial={{ opacity: 0 }} animate={{ opacity: 1 }}><button className="back-link" onClick={() => go('ranking')}>← Back to ranking</button><section className="compare-title"><div><p className="section-kicker">DECISION SUPPORT / SIDE BY SIDE</p><h2>Compare any two candidates</h2></div></section><div className="compare-selectors"><label><span>Candidate A</span><select value={a.id} onChange={event => updateCandidate(0, event.target.value)}>{candidates.map(candidate => <option key={candidate.id} value={candidate.id}>{candidate.name} · Rank {candidate.rank} · {candidate.score}</option>)}</select></label><label><span>Candidate B</span><select value={b.id} onChange={event => updateCandidate(1, event.target.value)}>{candidates.map(candidate => <option key={candidate.id} value={candidate.id}>{candidate.name} · Rank {candidate.rank} · {candidate.score}</option>)}</select></label></div><div className="compare-grid"><div className="compare-person"><span className="person-avatar">{a.initials}</span><div><strong>{a.name}</strong><small>Rank {String(a.rank).padStart(2, '0')} · {a.score}/100</small></div></div><div className="compare-person"><span className="person-avatar warm">{b.initials}</span><div><strong>{b.name}</strong><small>Rank {String(b.rank).padStart(2, '0')} · {b.score}/100</small></div></div>{requirements.map(requirement => <React.Fragment key={requirement.requirement_id}><div className="compare-cell"><span>{requirement.canonical_name} <small>({importanceLabel(requirement.importance)})</small></span><Chip type={matchFor(a, requirement).match_type} /></div><div className="compare-cell"><span>{requirement.canonical_name} <small>({importanceLabel(requirement.importance)})</small></span><Chip type={matchFor(b, requirement).match_type} /></div></React.Fragment>)}</div><div className="why-box"><span className="section-kicker">RANKING EXPLANATION</span><h3>{a.name} leads by {a.score - b.score} points</h3><p>{a.summary}</p></div></motion.div>;
}

function ShortlistScreen({ go, candidates, jobTitle, setSelectedId }) {
  return <motion.div className="workspace" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}><button className="back-link" onClick={() => go('ranking')}>← Back to ranking</button><section className="hero-line"><div><p className="section-kicker">TOP 3 EXPLANATIONS</p><h2>The shortlist</h2><p className="muted">Evidence-backed summaries for the top three candidates.</p></div><div className="shortlist-actions"><button className="outline-button" onClick={() => go('ranking')}>Full ranking</button><button className="dark-button" onClick={() => exportBrief(candidates, jobTitle)}>Export brief ↓</button></div></section><div className="shortlist-grid">{candidates.slice(0, 3).map(candidate => <article className="short-card" key={candidate.id}><div className="short-top"><span className="short-rank">{String(candidate.rank).padStart(2, '0')}</span><span className={`eligibility ${candidate.eligible ? 'good' : 'bad'}`}>{candidate.score}/100</span></div><h3>{candidate.name}</h3><span className="mono score-line">{candidate.keywordScore} KW · {candidate.semanticScore} SEM</span><p>{candidate.summary}</p><div className="risk"><strong>Eligibility</strong>{candidate.risk}</div><button className="text-button" onClick={() => { setSelectedId(candidate.id); go('detail'); }}>View breakdown →</button></article>)}</div></motion.div>;
}

function MethodologyScreen({ analysis, go }) {
  const m = analysis.methodology || {};
  const weights = analysis.scoring_weights || { keyword: 60, semantic: 40 };
  return <motion.div className="workspace" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}><button className="back-link" onClick={() => go('ranking')}>← Back to ranking</button><section className="hero-line"><div><p className="section-kicker">METHODOLOGY</p><h2>How candidates were scored</h2><p className="muted">{m.role_summary}</p></div></section>
    <div className="why-box"><span className="section-kicker">BLENDED APPROACH</span><h3>{weights.keyword}% keyword · {weights.semantic}% semantic</h3></div>
    <div className="detail-grid"><section className="evidence-list"><div className="panel-heading"><span>Keyword matching ({weights.keyword}%)</span></div><p className="excerpt">{m.keyword_summary}</p></section><section className="excerpt-panel"><div className="panel-heading"><span>Semantic matching ({weights.semantic}%)</span></div><p className="excerpt">{m.semantic_summary}</p></section></div>
  </motion.div>;
}

function EligibilityScreen({ analysis, go }) {
  const breakdown = analysis.eligibility_breakdown || {};
  const renderGroup = (title, items, className) => items?.length ? <section className="why-box"><span className="section-kicker">{title}</span><div className="eligibility-list">{items.map(item => <div key={item.name} className={`eligibility-item ${className}`}><strong>{item.name}</strong><p>{item.note}</p></div>)}</div></section> : null;
  return <motion.div className="workspace" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}><button className="back-link" onClick={() => go('ranking')}>← Back to ranking</button><section className="hero-line"><div><p className="section-kicker">ELIGIBILITY BREAKDOWN</p><h2>Must-have requirement gate</h2><p className="muted">JS ES6+, modern frontend framework, Node.js/Express, REST APIs, SQL/NoSQL, Git, CS/IT degree in progress.</p></div></section>
    {renderGroup('FULLY ELIGIBLE', breakdown.fully_eligible, 'good')}
    {renderGroup('BORDERLINE / PARTIALLY ELIGIBLE', breakdown.borderline, 'warn')}
    {renderGroup('NOT ELIGIBLE', breakdown.not_eligible, 'bad')}
    {analysis.bottom_line && <div className="why-box"><span className="section-kicker">BOTTOM LINE</span><p>{analysis.bottom_line}</p></div>}
  </motion.div>;
}

createRoot(document.getElementById('root')).render(<App />);
