import React, { useEffect, useMemo, useState } from 'react'
import apiClient from './api/client'
import { defaultCase, demoCases, DemoCase, DetectorView, RiskTier } from './data/demoCases'
import {
  AlertIcon,
  ArrowIcon,
  BuildingIcon,
  CheckIcon,
  ChevronIcon,
  ClockIcon,
  CopyIcon,
  DatabaseIcon,
  ExternalIcon,
  GraphIcon,
  LockIcon,
  MapPinIcon,
  NetworkIcon,
  PlayIcon,
  PriceIcon,
  RadarIcon,
  SearchIcon,
  ShieldIcon,
  SparkIcon,
} from './components/Icons'

const tierCopy: Record<RiskTier, { label: string; tone: string }> = {
  green: { label: 'Green', tone: 'green' },
  amber: { label: 'Amber', tone: 'amber' },
  red: { label: 'Red', tone: 'red' },
  red_cluster: { label: 'Red + cluster', tone: 'red' },
}

function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="brand" aria-label="ITC Radar">
      <span className="brand-mark"><RadarIcon size={compact ? 18 : 20} /></span>
      <span className="brand-name">ITC RADAR</span>
      {!compact && <span className="brand-engine">PACE engine</span>}
    </div>
  )
}

function TierBadge({ tier, compact = false }: { tier: RiskTier; compact?: boolean }) {
  const cfg = tierCopy[tier]
  return <span className={`tier-badge tier-${cfg.tone} ${compact ? 'is-compact' : ''}`}><span className="status-dot" />{cfg.label}</span>
}

function ScoreRing({ score, tier }: { score: number; tier: RiskTier }) {
  const radius = 42
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - score)
  const tone = tier === 'green' ? 'var(--green)' : tier === 'amber' ? 'var(--amber)' : 'var(--red)'
  return (
    <div className="score-ring" aria-label={`Risk score ${Math.round(score * 100)} out of 100`}>
      <svg viewBox="0 0 100 100" role="img">
        <circle className="score-track" cx="50" cy="50" r={radius} />
        <circle className="score-progress" cx="50" cy="50" r={radius} style={{ stroke: tone, strokeDasharray: circumference, strokeDashoffset: offset }} />
      </svg>
      <div className="score-number"><strong>{Math.round(score * 100)}</strong><span>risk</span></div>
    </div>
  )
}

function StatusPill({ status }: { status: DetectorView['status'] }) {
  const label = status === 'strong' ? 'Strong flag' : status === 'flag' ? 'Flag' : status === 'watch' ? 'Watch' : status === 'blocked' ? 'Suppressed' : 'Clear'
  return <span className={`detector-status detector-${status}`}>{status === 'clear' ? <CheckIcon size={14} /> : status === 'blocked' ? <LockIcon size={13} /> : <AlertIcon size={13} />}{label}</span>
}

function DetectorIcon({ id }: { id: DetectorView['id'] }) {
  if (id === 'D1') return <PriceIcon size={19} />
  if (id === 'D2a' || id === 'D2b') return <GraphIcon size={19} />
  if (id === 'D3') return <BuildingIcon size={19} />
  return <NetworkIcon size={19} />
}

function DetectorCard({ detector, active, onClick }: { detector: DetectorView; active: boolean; onClick: () => void }) {
  return (
    <button className={`detector-card ${active ? 'active' : ''}`} onClick={onClick}>
      <div className="detector-card-top">
        <span className="detector-icon"><DetectorIcon id={detector.id} /></span>
        <div className="detector-card-title"><span>{detector.id}</span><strong>{detector.name}</strong></div>
        <StatusPill status={detector.status} />
      </div>
      <p>{detector.short}</p>
      <div className="detector-metric"><span>{detector.metricLabel}</span><strong>{detector.metricValue}</strong></div>
      <div className="score-line"><span style={{ width: `${Math.max(2, detector.score * 100)}%` }} /></div>
    </button>
  )
}

function PriceScale({ demo }: { demo: DemoCase }) {
  const marker = Math.min(92, Math.max(8, Math.log2(Math.max(1, demo.price.multiple)) * 17 + 8))
  return (
    <div className="price-panel visual-panel">
      <div className="panel-eyebrow"><PriceIcon size={17} />D1 · Price closure</div>
      <div className="panel-headline-row">
        <div><h3>{demo.price.commodity}</h3><p>HSN {demo.price.hsn}</p></div>
        <strong className={demo.price.multiple >= 4 ? 'danger-text' : 'safe-text'}>{demo.price.multiple.toFixed(demo.price.multiple < 10 ? 1 : 0)}×</strong>
      </div>
      <div className="price-axis-wrap">
        <div className="price-axis-zone normal" />
        <div className="price-axis-zone review" />
        <div className="price-axis-zone extreme" />
        <span className="price-marker" style={{ left: `${marker}%` }}><i /></span>
      </div>
      <div className="price-axis-labels"><span>benchmark</span><span>review</span><span>extreme</span></div>
      <div className="compare-grid">
        <div><span>Reference median</span><strong>{demo.price.benchmark}</strong></div>
        <div><span>Declared unit value</span><strong>{demo.price.declared}</strong></div>
      </div>
      <p className="micro-note">Illustrative synthetic benchmark. The production design requires a versioned, auditable HSN reference distribution.</p>
    </div>
  )
}

function PremisesScene({ demo }: { demo: DemoCase }) {
  const blocked = demo.premises.areaM2 === null
  const risky = demo.premises.entityCount >= 5 && (demo.premises.areaM2 ?? 9999) < 1000
  const dots = Math.min(11, demo.premises.entityCount)
  return (
    <div className="premises-panel visual-panel">
      <div className="panel-eyebrow"><MapPinIcon size={17} />D3 · Premises aggregation</div>
      <div className={`site-map ${blocked ? 'map-blocked' : ''}`}>
        <svg viewBox="0 0 560 265" role="img" aria-label="Schematic premises footprint view">
          <defs>
            <pattern id={`grid-${demo.id}`} width="22" height="22" patternUnits="userSpaceOnUse"><path d="M22 0H0V22" fill="none" stroke="currentColor" strokeOpacity=".08" strokeWidth="1" /></pattern>
          </defs>
          <rect x="0" y="0" width="560" height="265" rx="20" fill={`url(#grid-${demo.id})`} />
          <path className="road wide" d="M-20 220 C130 170 215 226 330 166 S480 85 590 115" />
          <path className="road-line" d="M-20 220 C130 170 215 226 330 166 S480 85 590 115" />
          {!blocked && (
            <>
              <rect className={`footprint ${risky ? 'risky' : 'safe'}`} x={risky ? 220 : 108} y={risky ? 76 : 45} width={risky ? 118 : 338} height={risky ? 86 : 140} rx="15" />
              <rect className="footprint-inner" x={risky ? 235 : 126} y={risky ? 91 : 62} width={risky ? 88 : 302} height={risky ? 56 : 106} rx="10" />
              {Array.from({ length: dots }).map((_, i) => {
                const cols = risky ? 4 : 6
                const x0 = risky ? 250 : 150
                const y0 = risky ? 104 : 84
                const gapX = risky ? 21 : 43
                const gapY = risky ? 21 : 38
                return <g key={i}><circle className={`entity-pin ${risky ? 'pin-risky' : 'pin-safe'}`} cx={x0 + (i % cols) * gapX} cy={y0 + Math.floor(i / cols) * gapY} r="6" /><circle cx={x0 + (i % cols) * gapX} cy={y0 + Math.floor(i / cols) * gapY} r="11" className="pin-halo" /></g>
              })}
            </>
          )}
          {blocked && <g className="blocked-map"><circle cx="280" cy="122" r="38" /><path d="M280 99v35M280 151h.01" /><text x="280" y="202" textAnchor="middle">premises join suppressed</text></g>}
        </svg>
        <span className="map-caption">Schematic · synthetic premises geometry</span>
      </div>
      <div className="compare-grid three">
        <div><span>Cluster</span><strong>{demo.premises.clusterId}</strong></div>
        <div><span>Area</span><strong>{demo.premises.areaM2 ? `${demo.premises.areaM2.toLocaleString()} m²` : 'Not used'}</strong></div>
        <div><span>Registrations</span><strong>{demo.premises.entityCount}</strong></div>
      </div>
    </div>
  )
}

function NetworkScene({ demo }: { demo: DemoCase }) {
  const risky = demo.network.suspiciousNodes > 0
  const nodes = [
    [70, 95], [165, 48], [165, 145], [275, 88], [375, 44], [390, 150], [490, 94], [286, 188], [92, 190], [478, 188], [275, 28],
  ]
  const count = Math.min(nodes.length, Math.max(5, demo.network.directSuppliers > 10 ? 11 : demo.network.directSuppliers + 2))
  const edges = [[0,1],[0,2],[1,3],[2,3],[3,4],[3,5],[4,6],[5,6],[2,7],[7,5],[0,8],[5,9],[10,3]]
  return (
    <div className="network-panel visual-panel">
      <div className="panel-eyebrow"><NetworkIcon size={17} />D4 · Network topology</div>
      <div className="network-canvas">
        <svg viewBox="0 0 560 230" role="img" aria-label="Synthetic invoice network">
          {edges.map(([a,b], i) => a < count && b < count ? <line key={i} x1={nodes[a][0]} y1={nodes[a][1]} x2={nodes[b][0]} y2={nodes[b][1]} className={demo.network.cycle && [2,3,7].includes(i) ? 'cycle-edge' : 'network-edge'} /> : null)}
          {Array.from({ length: count }).map((_, i) => {
            const suspect = risky && i < Math.min(demo.network.suspiciousNodes, count)
            return <g key={i} className="network-node"><circle cx={nodes[i][0]} cy={nodes[i][1]} r={i === 6 ? 17 : 13} className={i === 6 ? 'recipient-node' : suspect ? 'suspicious-node' : 'clean-node'} /><text x={nodes[i][0]} y={nodes[i][1] + 4} textAnchor="middle">{i === 6 ? 'R' : `S${i + 1}`}</text></g>
          })}
        </svg>
        <div className="network-legend"><span><i className="legend-suspect" />flagged supplier</span><span><i className="legend-recipient" />recipient</span></div>
      </div>
      <div className="compare-grid three">
        <div><span>Direct suppliers</span><strong>{demo.network.directSuppliers}</strong></div>
        <div><span>Tax-origin depth</span><strong>{demo.network.originDepth ?? '—'}</strong></div>
        <div><span>Shared IDs</span><strong>{demo.network.sharedIdentifiers}</strong></div>
      </div>
    </div>
  )
}

function HeroPreview() {
  return (
    <div className="hero-preview" aria-hidden="true">
      <div className="preview-toolbar"><span /><span /><span /><div className="preview-title"><RadarIcon size={14} />RC-0001 · evidence workspace</div><i>synthetic</i></div>
      <div className="preview-body">
        <div className="raw-declaration">
          <span className="preview-label">Declarations</span>
          <h4>Refund claim</h4>
          <div className="raw-line long" /><div className="raw-line medium" /><div className="raw-line short" />
          <h4 className="raw-sub">Supplier cluster</h4>
          <div className="raw-line medium" /><div className="raw-line long" /><div className="raw-line tiny" />
          <div className="raw-stamp">paper trail ✓</div>
        </div>
        <div className="enhanced-evidence">
          <span className="preview-label"><SparkIcon size={14} />Evidence enhanced</span>
          <h4>Four signals converge</h4>
          <div className="evidence-line"><span className="tiny-icon red">₹</span><div><strong>31× price multiple</strong><small>outside HSN benchmark</small></div></div>
          <div className="evidence-line"><span className="tiny-icon orange">⌂</span><div><strong>11 entities · 96 m²</strong><small>shared premises cluster</small></div></div>
          <div className="evidence-line"><span className="tiny-icon purple">⌘</span><div><strong>0.4% cash / ITC</strong><small>weak upstream tax origin</small></div></div>
          <div className="preview-verdict"><span>Recommended tier</span><strong>RED + CLUSTER</strong></div>
        </div>
      </div>
    </div>
  )
}

function CasePicker({ selected, onSelect }: { selected: string; onSelect: (id: string) => void }) {
  const [open, setOpen] = useState(false)
  const current = demoCases.find(c => c.id === selected) ?? defaultCase
  return (
    <div className="case-picker-wrap">
      <button className="case-picker" onClick={() => setOpen(v => !v)}>
        <span className={`case-picker-dot ${current.type === 'positive' ? 'positive' : 'negative'}`} />
        <div><strong>{current.id}</strong><span>{current.company}</span></div>
        <ChevronIcon size={18} className={open ? 'rotate' : ''} />
      </button>
      {open && <div className="case-menu">
        <div className="case-menu-title">Synthetic case library <span>{demoCases.length} examples</span></div>
        {demoCases.map(c => (
          <button key={c.id} className={selected === c.id ? 'selected' : ''} onClick={() => { onSelect(c.id); setOpen(false) }}>
            <span className={`case-picker-dot ${c.type === 'positive' ? 'positive' : 'negative'}`} />
            <div><strong>{c.id} · {c.pattern}</strong><small>{c.company}</small></div>
            <TierBadge tier={c.tier} compact />
          </button>
        ))}
      </div>}
    </div>
  )
}

function App() {
  const [caseId, setCaseId] = useState(defaultCase.id)
  const [selectedDetector, setSelectedDetector] = useState<DetectorView['id']>('D1')
  const [running, setRunning] = useState(false)
  const [backendState, setBackendState] = useState<'checking' | 'connected' | 'fallback'>('checking')
  const [copied, setCopied] = useState(false)
  const [lastRun, setLastRun] = useState<number>(defaultCase.runtimeMs)

  const demo = useMemo(() => demoCases.find(c => c.id === caseId) ?? defaultCase, [caseId])
  const detector = demo.detectors.find(d => d.id === selectedDetector) ?? demo.detectors[0]

  useEffect(() => {
    let active = true
    apiClient.get('/health-proxy', { timeout: 7000 }).then(() => {
      if (active) setBackendState('connected')
    }).catch(() => {
      apiClient.get('../health', { timeout: 7000 }).then(() => active && setBackendState('connected')).catch(() => active && setBackendState('fallback'))
    })
    return () => { active = false }
  }, [])

  useEffect(() => {
    setSelectedDetector(demo.detectors.find(d => d.status === 'strong')?.id ?? demo.detectors.find(d => d.status === 'flag')?.id ?? 'D1')
  }, [caseId])

  async function runAnalysis() {
    setRunning(true)
    const started = performance.now()
    try {
      const response = await apiClient.post(`/demo/cases/${demo.id}/analyze`, {}, { timeout: 12000 })
      if (response.data?.case_id === demo.id) setBackendState('connected')
      const elapsed = Math.round(performance.now() - started)
      setLastRun(Math.max(180, elapsed))
    } catch {
      setBackendState('fallback')
      await new Promise(resolve => setTimeout(resolve, 620))
      setLastRun(demo.runtimeMs)
    } finally {
      setRunning(false)
    }
  }

  function copyReasoning() {
    const text = `${demo.id} — ${demo.company}\nTier: ${tierCopy[demo.tier].label}\n\n${demo.verdict}\n\nRecommended action: ${demo.action}`
    navigator.clipboard?.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1600)
    })
  }

  return (
    <main>
      <header className="top-shell">
        <nav className="nav-pill">
          <Logo />
          <div className="nav-links">
            <a href="#demo">Live demo</a>
            <a href="#method">Method</a>
            <a href="#guardrails">Guardrails</a>
            <a href="https://github.com/garvitjosh71035-lang/itc_radar_prototype" target="_blank" rel="noreferrer">GitHub <ExternalIcon size={13} /></a>
          </div>
          <a className="nav-cta" href="#demo">Open console <ArrowIcon size={16} /></a>
        </nav>
      </header>

      <section className="hero section-shell">
        <div className="hero-kicker"><SparkIcon size={16} />SIH 2026 · Open Innovation · synthetic prototype</div>
        <h1>Find the fraud<br/>the paperwork <em>can’t</em> hide.</h1>
        <p className="hero-copy">ITC Radar tests GST refund declarations against the parts of reality a fraud network does not fully control: <strong>market price, physical premises and transaction topology.</strong></p>
        <div className="hero-actions">
          <a href="#demo" className="primary-button"><PlayIcon size={16} />Run a synthetic case</a>
          <a href="#method" className="text-button">See the evidence model <ArrowIcon size={16} /></a>
        </div>
        <div className="hero-trust"><ShieldIcon size={17} /><span>Decision support, never automatic denial.</span><i />Role-gated<i />Geocode-gated<i />Human reviewed</div>
        <div className="hero-gradient" />
        <HeroPreview />
      </section>

      <section className="intro-strip section-shell">
        <div className="strip-label">What changes</div>
        <div className="strip-copy">From checking whether documents agree with each other<br/><em>to checking whether the declarations agree with reality.</em></div>
        <div className="strip-metrics"><span><strong>4</strong>independent detectors</span><span><strong>12</strong>system invariants</span><span><strong>{demoCases.length}</strong>demo scenarios</span></div>
      </section>

      <section id="demo" className="demo-section">
        <div className="section-shell">
          <div className="section-heading centered">
            <span className="eyebrow">Interactive prototype</span>
            <h2>An investigation workspace,<br/>not another score dashboard.</h2>
            <p>Pick a positive pattern or a hard negative. Every synthetic case shows not only what fired, but what the system deliberately refused to use.</p>
          </div>

          <div className="app-window">
            <div className="app-topbar">
              <Logo compact />
              <div className="app-search"><SearchIcon size={16} /><span>Search GSTIN, claim or cluster</span><kbd>⌘ K</kbd></div>
              <div className={`backend-chip state-${backendState}`}><span />{backendState === 'connected' ? 'API connected' : backendState === 'checking' ? 'Checking engine' : 'Demo fallback'}</div>
              <div className="avatar">IR</div>
            </div>

            <div className="app-body">
              <aside className="app-sidebar">
                <div className="sidebar-group"><span>Workspace</span><button className="active"><RadarIcon size={17} />Case analysis</button><button><GraphIcon size={17} />Risk queue <i>12</i></button><button><NetworkIcon size={17} />Network graph</button><button><MapPinIcon size={17} />Premises</button></div>
                <div className="sidebar-group"><span>Evidence</span><button><DatabaseIcon size={17} />Sources</button><button><ShieldIcon size={17} />Guardrails</button></div>
                <div className="sidebar-note"><LockIcon size={15} /><p><strong>Synthetic mode</strong>No real taxpayer data is included in this prototype.</p></div>
              </aside>

              <div className="workspace">
                <div className="workspace-header">
                  <div>
                    <div className="breadcrumb">Cases <span>/</span> {demo.id}</div>
                    <div className="title-line"><h2>{demo.company}</h2><TierBadge tier={demo.tier} /></div>
                    <p>{demo.headline}</p>
                  </div>
                  <div className="workspace-actions">
                    <CasePicker selected={caseId} onSelect={setCaseId} />
                    <button className={`run-button ${running ? 'running' : ''}`} onClick={runAnalysis} disabled={running}>{running ? <span className="spinner" /> : <PlayIcon size={15} />}{running ? 'Analyzing…' : 'Run analysis'}</button>
                  </div>
                </div>

                <div className="case-meta-row">
                  <div><span>Claim</span><strong>{demo.amount}</strong></div>
                  <div><span>Period</span><strong>{demo.period}</strong></div>
                  <div><span>Route</span><strong>{demo.route}</strong></div>
                  <div><span>Location</span><strong>{demo.district}</strong></div>
                  <div><span>Role</span><strong>{demo.declaredRole}</strong></div>
                  <div><span>Last run</span><strong><ClockIcon size={14} />{lastRun} ms</strong></div>
                </div>

                <div className="decision-row">
                  <div className="decision-card">
                    <ScoreRing score={demo.score} tier={demo.tier} />
                    <div className="decision-copy"><span>Fusion result</span><h3>{tierCopy[demo.tier].label}</h3><p>{demo.verdict}</p></div>
                  </div>
                  <div className="action-card"><span className="action-icon"><ShieldIcon size={21} /></span><div><span>Recommended officer action</span><p>{demo.action}</p></div><button onClick={copyReasoning} title="Copy summary"><CopyIcon size={17} />{copied ? 'Copied' : 'Copy'}</button></div>
                </div>

                <div className="detector-grid">
                  {demo.detectors.map(d => <DetectorCard key={d.id} detector={d} active={selectedDetector === d.id} onClick={() => setSelectedDetector(d.id)} />)}
                </div>

                <div className="selected-finding">
                  <div className="finding-icon"><DetectorIcon id={detector.id} /></div>
                  <div className="finding-copy"><div><span>{detector.id} · selected evidence</span><StatusPill status={detector.status} /></div><h3>{detector.finding}</h3>{detector.blockedReason && <p className="blocked-reason"><LockIcon size={14} />blocked_reason = <code>{detector.blockedReason}</code></p>}</div>
                  <div className="confidence-box"><span>confidence</span><strong>{Math.round(detector.confidence * 100)}%</strong></div>
                </div>

                <div className="evidence-visuals">
                  <PriceScale demo={demo} />
                  <PremisesScene demo={demo} />
                  <NetworkScene demo={demo} />
                </div>

                <div className="evidence-ledger">
                  <div className="ledger-heading"><div><span>Evidence ledger</span><h3>Traceable by construction.</h3></div><span className="ledger-count">{detector.evidence.length} refs for selected detector</span></div>
                  <div className="ledger-list">{detector.evidence.map((e, i) => <div key={i}><span>{String(i + 1).padStart(2, '0')}</span><p>{e}</p><small>recorded</small></div>)}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="method" className="method-section section-shell">
        <div className="section-heading split-heading"><div><span className="eyebrow">The evidence model</span><h2>Three realities.<br/>Four detectors.</h2></div><p>The core idea is deliberately simple: a fraudster can coordinate declarations, but not all of the external constraints those declarations imply.</p></div>
        <div className="method-grid">
          <article className="method-card card-price"><div className="method-number">01</div><div className="method-icon"><PriceIcon size={24} /></div><h3>Market reality</h3><p><strong>D1 · Price closure</strong> asks whether declared unit value sits inside a robust HSN benchmark distribution.</p><div className="method-example"><span>₹4,650/kg</span><i>vs</i><span>₹150/kg</span></div></article>
          <article className="method-card card-space"><div className="method-number">02</div><div className="method-icon"><BuildingIcon size={24} /></div><h3>Physical reality</h3><p><strong>D2 + D3</strong> test throughput density and shared-premises concentration using matched building footprints.</p><div className="tiny-building"><span /><span /><span /><span /><span /><span /><span /><span /><span /></div></article>
          <article className="method-card card-network"><div className="method-number">03</div><div className="method-icon"><NetworkIcon size={24} /></div><h3>Network reality</h3><p><strong>D4 · Topology</strong> surfaces named graph patterns: shallow tax origin, circular trading and shared identifiers.</p><div className="tiny-network"><i /><i /><i /><i /><i /><span /><span /><span /><span /></div></article>
        </div>
        <div className="closure-statement"><SparkIcon size={22} /><p><strong>Dual-constraint closure:</strong> inflate value by raising price and D1 binds; inflate quantity and capacity binds. Pure paper shells and coordinated networks are covered by D3 and D4.</p></div>
      </section>

      <section id="guardrails" className="guardrail-section">
        <div className="section-shell guardrail-shell">
          <div className="guardrail-copy"><span className="eyebrow light">Built to clear genuine cases</span><h2>Useful fraud detection needs a strong <em>“no.”</em></h2><p>The prototype keeps the workflow’s false-positive controls visible instead of hiding them behind a risk score.</p><div className="guardrail-badges"><span><ShieldIcon size={16} />Human-in-the-loop</span><span><LockIcon size={16} />Suppressed findings retained</span><span><CheckIcon size={16} />Hard negatives included</span></div></div>
          <div className="guardrail-list">
            {commonGuardrails.map((g, i) => <div key={i}><span>{String(i + 1).padStart(2, '0')}</span><p>{g}</p><CheckIcon size={18} /></div>)}
          </div>
        </div>
      </section>

      <section className="cases-section section-shell">
        <div className="section-heading centered"><span className="eyebrow">Demo library</span><h2>Fraud patterns <em>and</em> cases that must clear.</h2><p>A synthetic evaluation is only useful if it includes examples designed to defeat naive detectors.</p></div>
        <div className="case-showcase">
          {demoCases.map(c => <button key={c.id} className="showcase-card" onClick={() => { setCaseId(c.id); document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth' }) }}><div className="showcase-top"><span className={`case-type ${c.type === 'positive' ? 'positive' : 'negative'}`}>{c.type === 'positive' ? 'Injected pattern' : 'Hard negative'}</span><TierBadge tier={c.tier} compact /></div><span className="showcase-id">{c.id}</span><h3>{c.headline}</h3><p>{c.description}</p><div className="showcase-link">Open case <ArrowIcon size={15} /></div></button>)}
        </div>
      </section>

      <section className="closing-section section-shell">
        <div className="closing-card"><div className="closing-spark"><SparkIcon size={44} /></div><span className="eyebrow">ITC Radar · PACE engine</span><h2>From declarations to ground reality.<br/>From suspicion to explainable evidence.</h2><p>Built as a transparent, synthetic SIH prototype. Production use would require GSTN-authorised transaction data, calibrated thresholds and practitioner-validated legal integration.</p><div className="hero-actions"><a href="#demo" className="primary-button">Open the console <ArrowIcon size={16} /></a><a href="https://github.com/garvitjosh71035-lang/itc_radar_prototype" target="_blank" rel="noreferrer" className="text-button">View repository <ExternalIcon size={15} /></a></div></div>
      </section>

      <footer className="footer section-shell"><Logo compact /><p>ITC Radar prototype · SIH 2026 · Synthetic demonstration only</p><div><a href="#method">Method</a><a href="#guardrails">Guardrails</a><a href="https://github.com/garvitjosh71035-lang/itc_radar_prototype" target="_blank" rel="noreferrer">GitHub</a></div></footer>
    </main>
  )
}

const commonGuardrails = defaultCase.guardrails

export default App
