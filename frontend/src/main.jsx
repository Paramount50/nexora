import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { AnimatePresence, motion } from 'framer-motion';
import './styles.css';
import './dark.css';

const importanceLabel = (importance) => importance === 'required' ? 'Must-have' : 'Good-to-have';
const matchLabel = { exact: 'Exact', alias: 'Alias', related: 'Related', fuzzy: 'Inferred', none: 'Missing' };

function toCandidate(item) {
  const results = item.requirement_results || [];
  const firstEvidence = results.find(result => result.evidence_text?.length)?.evidence_text?.[0];
  return {
    ...item,
    id: item.candidate_id,
    name: item.candidate_name || item.candidate_id,
    initials: (item.candidate_name || item.candidate_id).split(/\s+/).map(part => part[0]).join('').slice(0, 2).toUpperCase(),
    score: Math.round(item.final_score || 0),
    role: item.resume_source || 'Uploaded resume',
    summary: item.fit?.weighted_requirement_score ? `Evidence-backed fit score ${Math.round(item.final_score)} with ${Math.round((item.mandatory_coverage || 0) * 100)}% must-have coverage.` : 'No fit summary available.',
    risk: item.missing_requirements?.length ? item.missing_requirements.join(', ') : 'No missing requirements',
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
    <span className="legend-label">{mustHave} must-have · {goodToHave} good-to-have · evidence remains traceable</span>
    <span><i className="legend-swatch exact" />Exact / alias</span><span><i className="legend-swatch related" />Related</span><span><i className="legend-swatch semantic" />Inferred</span><span><i className="legend-swatch missing" />Missing</span>
  </div>;
}
function exportBrief(candidates, jobTitle) {
  const lines = ['NEXORA SHORTLIST', jobTitle, '', 'Top candidates'];
  candidates.slice(0, 3).forEach(candidate => {
    lines.push(`#${candidate.rank} ${candidate.name} — fit ${candidate.score} — ${candidate.eligible ? 'Eligible' : 'Needs review'}`);
    lines.push(candidate.summary);
    lines.push(`Watch: ${candidate.risk}`);
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
  const [screen, setScreen] = useState('intake');
  const [analysis, setAnalysis] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [compareIds, setCompareIds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const candidates = useMemo(() => (analysis?.rankings || []).map(toCandidate), [analysis]);
  const requirements = analysis?.job?.requirements || [];
  const selected = candidates.find(candidate => candidate.id === selectedId) || candidates[0];
  const go = (next) => setScreen(next);

  async function analyze(jdFile, resumeFiles, mode) {
    setLoading(true);
    setError('');
    const form = new FormData();
    form.append('jd', jdFile);
    resumeFiles.forEach(file => form.append('resumes', file));
    form.append('mode', mode);
    try {
      const response = await fetch('/api/analyze', { method: 'POST', body: form });
      const responseText = await response.text();
      let payload;
      try {
        payload = responseText ? JSON.parse(responseText) : {};
      } catch {
        throw new Error(`The analysis server returned an invalid response (${response.status}). Is the FastAPI backend running on port 8000?`);
      }
      if (!response.ok) throw new Error(payload.detail || 'The analysis could not be completed.');
      setAnalysis(payload);
      const normalized = (payload.rankings || []).map(toCandidate);
      setSelectedId(normalized[0]?.id || null);
      setCompareIds(normalized.slice(0, 2).map(candidate => candidate.id));
      setScreen('ranking');
    } catch (requestError) {
      setError(requestError.message || 'The analysis could not be completed.');
    } finally {
      setLoading(false);
    }
  }

  return <div className="app-shell"><main className="main-content">
    <header className="topbar"><div className="topbar-brand"><div className="brand-mark">N</div><div><p className="eyebrow">NEXORA / {screen === 'intake' ? 'NEW ANALYSIS' : 'ANALYSIS COMPLETE'}</p><h1>{screen === 'intake' ? 'Resume intelligence' : analysis?.job?.job_title || 'Candidate ranking'}</h1></div></div>
      {analysis && <nav className="top-nav"><button className={screen === 'ranking' || screen === 'detail' || screen === 'compare' ? 'nav-link active' : 'nav-link'} onClick={() => go('ranking')}>All candidates</button><button className={screen === 'shortlist' ? 'nav-link active' : 'nav-link'} onClick={() => go('shortlist')}>Shortlist</button><button className="nav-link" onClick={() => go('intake')}>New analysis</button></nav>}
      <div className="top-actions">{analysis && <><span className="live-dot">●</span><span>{analysis.candidate_count} candidates analyzed</span></>}</div>
    </header>
    {error && <div className="error-banner">{error}</div>}
    <AnimatePresence mode="wait">
      {screen === 'ranking' && analysis && <RankingScreen key="ranking" {...{ candidates, requirements, selectedId, setSelectedId, go }} />}
      {screen === 'detail' && selected && <DetailScreen key="detail" candidate={selected} requirements={requirements} go={go} />}
      {screen === 'compare' && analysis && <CompareScreen key="compare" go={go} candidates={candidates} requirements={requirements} compareIds={compareIds} setCompareIds={setCompareIds} />}
      {screen === 'shortlist' && analysis && <ShortlistScreen key="shortlist" go={go} candidates={candidates} jobTitle={analysis.job?.job_title} setSelectedId={setSelectedId} />}
      {screen === 'intake' && <IntakeScreen key="intake" onAnalyze={analyze} loading={loading} />}
    </AnimatePresence>
  </main></div>;
}

function RankingScreen({ candidates, requirements, selectedId, setSelectedId, go }) {
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('All candidates');
  const filtered = candidates.filter(candidate => candidate.name.toLowerCase().includes(query.toLowerCase()) && (filter === 'All candidates' || (filter === 'Eligible' ? candidate.eligible : !candidate.eligible)));
  const eligibleCount = candidates.filter(candidate => candidate.eligible).length;
  const mustHaveCount = requirements.filter(requirement => requirement.importance === 'required').length;
  return <motion.div className="workspace" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
    <section className="hero-line"><div><p className="section-kicker">SHORTLIST / {candidates.length} CANDIDATES</p><h2>Evidence-led ranking</h2><p className="muted">Must-have requirements gate eligibility; good-to-have skills refine the fit score.</p></div><div className="hero-stats"><div><strong>{eligibleCount}</strong><span>eligible</span></div><div><strong>{mustHaveCount}</strong><span>must-haves</span></div><div><strong>{candidates[0]?.score || 0}</strong><span>top score</span></div></div></section>
    <div className="control-row"><div className="search"><Icon>⌕</Icon><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Search candidates" /></div><select value={filter} onChange={event => setFilter(event.target.value)}><option>All candidates</option><option>Eligible</option><option>Needs review</option></select><button className="outline-button" onClick={() => go('compare')}>Compare candidates <span>↗</span></button><button className="dark-button" onClick={() => go('shortlist')}>View shortlist</button></div><CoverageLegend requirements={requirements} />
    <div className="table-wrap"><div className="table-head"><span>Rank / candidate</span><span>Eligibility</span><span>Fit</span><span>Coverage</span><span>Evidence quality</span><span> </span></div>{filtered.map((candidate, index) => <motion.button key={candidate.id} className={`candidate-row ${index === 0 ? 'top-row' : ''} ${selectedId === candidate.id ? 'selected' : ''}`} onClick={() => { setSelectedId(candidate.id); go('detail'); }} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.05 }}><div className="candidate-cell"><span className="rank-number">{String(candidate.rank).padStart(2, '0')}</span><span className="person-avatar">{candidate.initials}</span><span><strong>{candidate.name}</strong><small>{candidate.role}</small></span></div><div><span className={`eligibility ${candidate.eligible ? 'good' : 'bad'}`}>{candidate.eligible ? 'Eligible' : 'Missing required'}</span></div><div className="score">{candidate.score}</div><div className="coverage"><div className="segmented">{requirements.map(requirement => { const result = candidate.requirement_results?.find(item => item.canonical_name === requirement.canonical_name); return <i key={requirement.requirement_id} className={`segment ${result?.match_type || 'none'}`} title={`${requirement.canonical_name}: ${importanceLabel(requirement.importance)} / ${result?.match_type || 'missing'}`} />; })}</div><small>{candidate.matches.filter(match => match[1] !== 'none').length}/{requirements.length} covered</small></div><div className="row-signals">{evidenceSignals(candidate).map(([source, skill, type]) => <EvidenceSignal key={`${source}-${skill}`} type={type}>{source} · {skill}</EvidenceSignal>)}</div><span className="row-arrow">→</span></motion.button>)}</div>
    <div className="table-footer"><span>Showing {filtered.length} of {candidates.length} candidates</span><button className="text-button view-all" onClick={() => { setQuery(''); setFilter('All candidates'); }}>View all candidates →</button><span><b>Score basis:</b> must-have priority + evidence strength</span></div>
  </motion.div>;
}

function DetailScreen({ candidate: c, requirements, go }) {
  const [req, setReq] = useState(requirements[0]?.canonical_name || '');
  const selectedResult = c.requirement_results?.find(result => result.canonical_name === req) || c.requirement_results?.[0];
  return <motion.div className="workspace" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }}><button className="back-link" onClick={() => go('ranking')}>← Back to ranking</button><section className="detail-header"><div><p className="section-kicker">CANDIDATE / {String(c.rank).padStart(2, '0')}</p><h2>{c.name}</h2><p className="muted">{c.role} · Evidence review</p></div><div className="detail-score"><span>FIT SCORE</span><strong>{c.score}</strong><span className={`eligibility ${c.eligible ? 'good' : 'bad'}`}>{c.eligible ? 'Eligible' : 'Missing required'}</span></div></section><div className="detail-grid"><section className="evidence-list"><div className="panel-heading"><span>Requirement breakdown</span><span className="muted">{requirements.length} requirements</span></div>{requirements.map(requirement => { const result = c.requirement_results?.find(item => item.canonical_name === requirement.canonical_name) || { match_type: 'none', missing: true }; return <button className={`requirement-row ${req === requirement.canonical_name ? 'active' : ''}`} key={requirement.requirement_id} onClick={() => setReq(requirement.canonical_name)}><span><strong>{requirement.canonical_name}</strong><small>{importanceLabel(requirement.importance)} · {requirement.category}</small></span><span className="strength-label">{evidenceStrength(result.match_type)}</span><Chip type={result.match_type} /></button>; })}</section><section className="excerpt-panel"><div className="panel-heading"><span>Evidence excerpt</span><span className="source-tag">{selectedResult?.importance === 'required' ? 'MUST-HAVE' : 'GOOD-TO-HAVE'}</span></div><div className="excerpt-meta"><span className="mono">MATCHED EVIDENCE / {req.toUpperCase()}</span><span className="confidence">Confidence {selectedResult ? Number(selectedResult.confidence || selectedResult.fused_score || 0).toFixed(2) : '0.00'}</span></div><p className="excerpt">{selectedResult?.evidence_text?.[0] || 'No supporting evidence found in this resume.'}</p><div className="annotation"><span className="annotation-line" /><div><strong>Why this matters</strong><p>{selectedResult?.importance === 'required' ? 'This is a must-have requirement and contributes to eligibility.' : 'This is a good-to-have requirement and refines fit after must-haves are considered.'}</p></div></div></section></div></motion.div>;
}

function CompareScreen({ go, candidates, requirements, compareIds, setCompareIds }) {
  const a = candidates.find(candidate => candidate.id === compareIds[0]) || candidates[0];
  const b = candidates.find(candidate => candidate.id === compareIds[1]) || candidates[1] || candidates[0];
  const updateCandidate = (side, id) => setCompareIds(current => side === 0 ? [id, current[1]] : [current[0], id]);
  const matchFor = (candidate, requirement) => candidate?.requirement_results?.find(result => result.canonical_name === requirement.canonical_name) || { match_type: 'none' };
  if (!a || !b) return null;
  return <motion.div className="workspace" initial={{ opacity: 0 }} animate={{ opacity: 1 }}><button className="back-link" onClick={() => go('ranking')}>← Back to ranking</button><section className="compare-title"><div><p className="section-kicker">DECISION SUPPORT / SIDE BY SIDE</p><h2>Compare any two candidates</h2><p className="muted">Must-have gaps are visible before good-to-have overlap.</p></div></section><div className="compare-selectors"><label><span>Candidate A</span><select value={a.id} onChange={event => updateCandidate(0, event.target.value)}>{candidates.map(candidate => <option key={candidate.id} value={candidate.id}>{candidate.name} · Rank {candidate.rank}</option>)}</select></label><label><span>Candidate B</span><select value={b.id} onChange={event => updateCandidate(1, event.target.value)}>{candidates.map(candidate => <option key={candidate.id} value={candidate.id}>{candidate.name} · Rank {candidate.rank}</option>)}</select></label></div><div className="compare-grid"><div className="compare-person"><span className="person-avatar">{a.initials}</span><div><strong>{a.name}</strong><small>Rank {String(a.rank).padStart(2, '0')} · Fit {a.score}</small></div></div><div className="compare-person"><span className="person-avatar warm">{b.initials}</span><div><strong>{b.name}</strong><small>Rank {String(b.rank).padStart(2, '0')} · Fit {b.score}</small></div></div>{requirements.map(requirement => <React.Fragment key={requirement.requirement_id}><div className="compare-cell"><span>{requirement.canonical_name} <small>({importanceLabel(requirement.importance)})</small></span><Chip type={matchFor(a, requirement).match_type} /></div><div className="compare-cell"><span>{requirement.canonical_name} <small>({importanceLabel(requirement.importance)})</small></span><Chip type={matchFor(b, requirement).match_type} /></div></React.Fragment>)}</div><div className="why-box"><span className="section-kicker">RANKING EXPLANATION</span><h3>{a.name} leads by {a.score - b.score} points</h3><p>Must-have eligibility is evaluated first. Good-to-have skills refine fit only after that priority is respected.</p></div></motion.div>;
}

function ShortlistScreen({ go, candidates, jobTitle, setSelectedId }) { return <motion.div className="workspace" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}><button className="back-link" onClick={() => go('ranking')}>← Back to all candidates</button><section className="hero-line"><div><p className="section-kicker">SHAREABLE BRIEF / TOP THREE</p><h2>The shortlist</h2><p className="muted">A concise, evidence-backed view for the hiring manager.</p></div><div className="shortlist-actions"><button className="outline-button" onClick={() => go('ranking')}>View all candidates</button><button className="dark-button" onClick={() => exportBrief(candidates, jobTitle)}>Export brief ↓</button></div></section><div className="shortlist-grid">{candidates.slice(0, 3).map(candidate => <article className="short-card" key={candidate.id}><div className="short-top"><span className="short-rank">{String(candidate.rank).padStart(2, '0')}</span><span className={`eligibility ${candidate.eligible ? 'good' : 'bad'}`}>{candidate.eligible ? 'Eligible' : 'Needs review'}</span></div><h3>{candidate.name}</h3><span className="mono score-line">{candidate.score} <em>FIT SCORE</em></span><p>{candidate.summary}</p><div className="risk"><strong>Watch</strong>{candidate.risk}</div><button className="text-button" onClick={() => { setSelectedId(candidate.id); go('detail'); }}>Inspect evidence →</button></article>)}</div></motion.div>; }

function IntakeScreen({ onAnalyze, loading }) {
  const [jdFile, setJdFile] = useState(null);
  const [resumeFiles, setResumeFiles] = useState([]);
  const [mode, setMode] = useState('hybrid');
  return <motion.div className="workspace intake" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}><p className="section-kicker">NEXORA / NEW ANALYSIS</p><h2>Start with the role.</h2><p className="muted intro">Add the job description and candidate resumes. Nexora will map every ranking decision back to evidence in these files.</p><div className="drop-grid"><div className={`dropzone ${jdFile ? 'uploaded' : ''}`}><input className="file-input" type="file" accept=".pdf,.docx,.txt" onChange={event => setJdFile(event.target.files?.[0] || null)} /><span className="drop-icon">↳</span><h3>{jdFile?.name || 'Job description'}</h3><p>{jdFile ? 'Ready to analyze' : 'PDF, DOCX or TXT · one file'}</p><button className="outline-button" onClick={event => event.currentTarget.parentElement.querySelector('input').click()}>{jdFile ? 'Replace file' : 'Choose file'}</button></div><div className={`dropzone ${resumeFiles.length ? 'uploaded' : ''}`}><input className="file-input" type="file" accept=".pdf,.docx,.txt,.xml" multiple onChange={event => setResumeFiles(Array.from(event.target.files || []))} /><span className="drop-icon">⊞</span><h3>{resumeFiles.length ? `${resumeFiles.length} resumes added` : 'Candidate resumes'}</h3><p>{resumeFiles.length ? 'Ready to analyze' : 'PDF, DOCX, TXT or XML · multiple files'}</p><button className="outline-button" onClick={event => event.currentTarget.parentElement.querySelector('input').click()}>{resumeFiles.length ? 'Replace files' : 'Choose files'}</button></div></div><div className="intake-footer"><label className="mode-picker"><span>Scoring mode</span><select value={mode} onChange={event => setMode(event.target.value)}><option value="hybrid">Hybrid evidence</option><option value="keyword">Keyword evidence</option><option value="semantic">Semantic evidence</option></select></label><span><b>{resumeFiles.length}</b> candidates added</span><button className="dark-button" disabled={!jdFile || !resumeFiles.length || loading} onClick={() => onAnalyze(jdFile, resumeFiles, mode)}>{loading ? 'Analyzing…' : 'Start analysis'} <span>→</span></button></div></motion.div>;
}

createRoot(document.getElementById('root')).render(<App />);
