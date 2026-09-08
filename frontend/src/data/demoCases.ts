export type RiskTier = 'green' | 'amber' | 'red' | 'red_cluster'
export type DetectorStatus = 'clear' | 'flag' | 'strong' | 'blocked' | 'watch'

export interface DetectorView {
  id: 'D1' | 'D2a' | 'D2b' | 'D3' | 'D4'
  name: string
  short: string
  score: number
  confidence: number
  status: DetectorStatus
  finding: string
  blockedReason?: string
  metricLabel: string
  metricValue: string
  evidence: string[]
}

export interface PremisesView {
  clusterId: string
  entityCount: number
  areaM2: number | null
  landCover: string
  roadClass: string
  geocode: string
  joinStatus: string
  attributedCrore: number | null
  densityMultiple: number | null
}

export interface NetworkView {
  directSuppliers: number
  suspiciousNodes: number
  originDepth: number | null
  cashToItc: number | null
  sharedIdentifiers: number
  cycle: boolean
}

export interface PriceView {
  hsn: string
  commodity: string
  multiple: number
  benchmark: string
  declared: string
}

export interface DemoCase {
  id: string
  gstin: string
  company: string
  pattern: string
  type: 'positive' | 'hard-negative'
  headline: string
  description: string
  amount: string
  period: string
  route: string
  district: string
  declaredRole: string
  tier: RiskTier
  score: number
  action: string
  verdict: string
  runtimeMs: number
  detectors: DetectorView[]
  premises: PremisesView
  network: NetworkView
  price: PriceView
  guardrails: string[]
}

const commonGuardrails = [
  'Physical findings cannot create an adverse tier without D1 or D4 corroboration.',
  'Street, locality-centroid and unresolved geocodes cannot support adverse physical findings.',
  'Role-gated traders, job-workers and service providers are not judged as factories.',
  'D2b stays blocked wherever a sector capacity constant lacks a citable source.',
]

export const demoCases: DemoCase[] = [
  {
    id: 'RC-0001',
    gstin: 'EXP0001SYNTH26',
    company: 'Aster Exports LLP',
    pattern: 'Flagship synthetic case',
    type: 'positive',
    headline: 'Over-invoicing + shared-premises shell cluster',
    description: 'Merchant exporter receives inflated invoices from a newly formed supplier cluster. Eleven matched manufacturers resolve to one small premises cluster and share weak tax origin.',
    amount: '₹42.0 cr',
    period: 'Apr–Jun 2026',
    route: 'Zero-rated export refund',
    district: 'Surat, Gujarat',
    declaredRole: 'Trader · no warehousing',
    tier: 'red_cluster',
    score: 0.97,
    action: 'Physical verification before disbursement; inspect the supplier cluster and retain drafted reasons for officer review.',
    verdict: 'Four independent signals converge. The claimant itself is role-gated from physical tests; the adverse evidence comes from matched upstream manufacturers.',
    runtimeMs: 842,
    detectors: [
      {
        id: 'D1', name: 'Price closure', short: 'Economic plausibility', score: 0.99, confidence: 0.96, status: 'strong',
        finding: 'Two export lines sit at approximately 28× and 31× the synthetic HSN benchmark median.',
        metricLabel: 'Highest price multiple', metricValue: '31×',
        evidence: ['Synthetic invoice lines', 'Demo HS-6 benchmark v2026.1', 'UQC normalisation: exact'],
      },
      {
        id: 'D2a', name: 'Capacity closure', short: 'Throughput density', score: 0.99, confidence: 0.93, status: 'strong',
        finding: '₹380 cr attributed to a 96 m² cluster is about 790× the district × sector median density.',
        metricLabel: 'Density multiple', metricValue: '≈790×',
        evidence: ['Movement-derived attribution', 'Cluster PC-4471 · 96 m²', 'Synthetic district-sector benchmark'],
      },
      {
        id: 'D2b', name: 'Physical capacity', short: 'Explainable engineering model', score: 0.00, confidence: 1.00, status: 'blocked',
        finding: 'No D2b adverse finding emitted because sector capacity constants are intentionally unsourced in the prototype.',
        blockedReason: 'unsourced_parameter', metricLabel: 'Safety gate', metricValue: 'Blocked',
        evidence: ['Invariant I9', 'Capacity parameter table: calibration pending'],
      },
      {
        id: 'D3', name: 'Premises aggregation', short: 'Ground reality', score: 0.96, confidence: 0.94, status: 'strong',
        finding: 'Eleven goods-supplying registrations resolve to 96 m²: roughly one entity per 8.7 m².',
        metricLabel: 'Entity density', metricValue: '1 / 8.7 m²',
        evidence: ['Matched rooftop/building-centroid geocodes', 'Dissolved premises cluster', 'Synthetic Overture-style footprint record'],
      },
      {
        id: 'D4', name: 'Network topology', short: 'Syndicate structure', score: 0.94, confidence: 0.91, status: 'strong',
        finding: 'The supplier graph has shallow tax origin, 0.4% cash-to-ITC, high billing velocity and shared identifiers.',
        metricLabel: 'Cash / ITC', metricValue: '0.4%',
        evidence: ['Synthetic invoice graph', 'Shared bank hashes: 3 across 11 entities', 'Depth-3 traversal'],
      },
    ],
    premises: { clusterId: 'PC-4471', entityCount: 11, areaM2: 96, landCover: 'Built-up · residential context', roadClass: 'Residential lane', geocode: '7 rooftop · 4 building centroid', joinStatus: '11 matched', attributedCrore: 380, densityMultiple: 790 },
    network: { directSuppliers: 18, suspiciousNodes: 11, originDepth: 0, cashToItc: 0.004, sharedIdentifiers: 3, cycle: false },
    price: { hsn: '5407', commodity: 'Synthetic woven fabric', multiple: 31, benchmark: '₹150/kg median', declared: '₹4,650/kg' },
    guardrails: commonGuardrails,
  },
  {
    id: 'P2-OVER',
    gstin: 'OVERINV002SYN26',
    company: 'Northstar Trading Co.',
    pattern: 'P2 · Over-invoiced supply',
    type: 'positive',
    headline: 'A price anomaly without physical corroboration',
    description: 'A deliberately inflated invoice is caught by D1, but the premises and network signals remain ordinary. The fusion layer therefore stops at Amber.',
    amount: '₹8.4 cr', period: 'Jul 2026', route: 'SEZ supply refund', district: 'Mumbai, Maharashtra', declaredRole: 'Trader',
    tier: 'amber', score: 0.67,
    action: 'Allow normal processing subject to post-disbursement audit; request commercial justification for the price outlier if reviewed.',
    verdict: 'D1 alone is not enough for an adverse physical-verification tier. This case demonstrates the corroboration rule rather than maximum recall.', runtimeMs: 386,
    detectors: [
      { id: 'D1', name: 'Price closure', short: 'Economic plausibility', score: 0.98, confidence: 0.94, status: 'strong', finding: 'Declared unit value is approximately 20× the synthetic HSN median.', metricLabel: 'Price multiple', metricValue: '20×', evidence: ['Synthetic invoice line', 'Demo HSN benchmark v2026.1'] },
      { id: 'D2a', name: 'Capacity closure', short: 'Throughput density', score: 0.00, confidence: 1.00, status: 'blocked', finding: 'The claimant is a trader with no warehousing; physical throughput attribution is not applicable.', blockedReason: 'role_gate', metricLabel: 'Applicability', metricValue: 'Role-gated', evidence: ['P1 declared-role gate'] },
      { id: 'D2b', name: 'Physical capacity', short: 'Explainable engineering model', score: 0.00, confidence: 1.00, status: 'blocked', finding: 'Not applicable to a trader without goods-handling premises.', blockedReason: 'role_gate', metricLabel: 'Applicability', metricValue: 'Role-gated', evidence: ['P1 declared-role gate'] },
      { id: 'D3', name: 'Premises aggregation', short: 'Ground reality', score: 0.00, confidence: 1.00, status: 'blocked', finding: 'No factory-existence inference is attempted against a pure trader.', blockedReason: 'role_gate', metricLabel: 'Applicability', metricValue: 'Role-gated', evidence: ['P1 declared-role gate'] },
      { id: 'D4', name: 'Network topology', short: 'Syndicate structure', score: 0.18, confidence: 0.88, status: 'clear', finding: 'Supplier relationships show normal depth, no cycles and no meaningful shared-identifier cluster.', metricLabel: 'Tax-origin depth', metricValue: '4', evidence: ['Synthetic invoice graph'] },
    ],
    premises: { clusterId: 'N/A', entityCount: 1, areaM2: null, landCover: 'Not evaluated', roadClass: 'Not evaluated', geocode: 'Role-gated', joinStatus: 'Not joined', attributedCrore: null, densityMultiple: null },
    network: { directSuppliers: 6, suspiciousNodes: 0, originDepth: 4, cashToItc: 0.18, sharedIdentifiers: 0, cycle: false },
    price: { hsn: '5407', commodity: 'Synthetic woven fabric', multiple: 20, benchmark: '₹150/kg median', declared: '₹3,000/kg' },
    guardrails: commonGuardrails,
  },
  {
    id: 'P3-CYCLE',
    gstin: 'CYCLE003SYNTH26',
    company: 'Orbit Components Pvt. Ltd.',
    pattern: 'P3 · Circular trading',
    type: 'positive',
    headline: 'Closed invoice loop with weak cash tax origin',
    description: 'A three-entity cycle inflates turnover while physical capacity is not independently suspicious. D4 surfaces the named graph pattern and fusion stays at Amber.',
    amount: '₹16.2 cr', period: 'Aug 2026', route: 'ITC accumulation sweep', district: 'Noida, Uttar Pradesh', declaredRole: 'Manufacturer',
    tier: 'amber', score: 0.71,
    action: 'Queue for network-focused audit and reconcile the circular invoice chain before any stronger intervention.',
    verdict: 'The graph is suspicious, but the prototype refuses to turn topology alone into a Red physical-verification tier.', runtimeMs: 521,
    detectors: [
      { id: 'D1', name: 'Price closure', short: 'Economic plausibility', score: 0.24, confidence: 0.90, status: 'clear', finding: 'Unit prices remain inside the synthetic HSN reference band.', metricLabel: 'Price multiple', metricValue: '1.2×', evidence: ['Synthetic invoice lines', 'Demo HSN benchmark v2026.1'] },
      { id: 'D2a', name: 'Capacity closure', short: 'Throughput density', score: 0.31, confidence: 0.86, status: 'clear', finding: 'Declared throughput density is not an outlier for the district × sector stratum.', metricLabel: 'Density multiple', metricValue: '2.1×', evidence: ['Movement-derived attribution', 'Synthetic district-sector benchmark'] },
      { id: 'D2b', name: 'Physical capacity', short: 'Explainable engineering model', score: 0.00, confidence: 1.00, status: 'blocked', finding: 'Engineering capacity parameters remain calibration-only in this prototype.', blockedReason: 'unsourced_parameter', metricLabel: 'Safety gate', metricValue: 'Blocked', evidence: ['Invariant I9'] },
      { id: 'D3', name: 'Premises aggregation', short: 'Ground reality', score: 0.20, confidence: 0.91, status: 'clear', finding: 'The registered manufacturer occupies an industrial footprint with adequate space.', metricLabel: 'Entity density', metricValue: '1 / 780 m²', evidence: ['Synthetic footprint record'] },
      { id: 'D4', name: 'Network topology', short: 'Syndicate structure', score: 0.98, confidence: 0.95, status: 'strong', finding: 'A→B→C→A circular trade loop is present with shallow cash-tax origin.', metricLabel: 'Named pattern', metricValue: '3-node cycle', evidence: ['Depth-3 synthetic invoice graph', 'Cycle detection'] },
    ],
    premises: { clusterId: 'PC-3110', entityCount: 1, areaM2: 780, landCover: 'Industrial built-up', roadClass: 'Secondary road', geocode: 'Rooftop', joinStatus: 'Matched', attributedCrore: 16.2, densityMultiple: 2.1 },
    network: { directSuppliers: 4, suspiciousNodes: 3, originDepth: 1, cashToItc: 0.015, sharedIdentifiers: 0, cycle: true },
    price: { hsn: '8538', commodity: 'Electrical components', multiple: 1.2, benchmark: '₹820/kg median', declared: '₹984/kg' },
    guardrails: commonGuardrails,
  },
  {
    id: 'P4-VOLUME',
    gstin: 'BULK004SYNTH26',
    company: 'Delta Recyclers',
    pattern: 'P4 · Volume inflation',
    type: 'positive',
    headline: 'Bulk throughput overwhelms a small registered site',
    description: 'Scrap-metal quantity is priced plausibly, but movement-derived value and mass imply throughput far beyond the small premises. D4 adds registration-velocity corroboration.',
    amount: '₹27.5 cr', period: 'Jun–Aug 2026', route: 'Inverted-duty refund', district: 'Faridabad, Haryana', declaredRole: 'Manufacturer',
    tier: 'red', score: 0.91,
    action: 'Request physical verification of the declared goods-handling premises before disbursement.',
    verdict: 'This is the fraud mode where capacity closure earns its place: D1 is clean, while D2a is strong and D4 independently corroborates risk.', runtimeMs: 706,
    detectors: [
      { id: 'D1', name: 'Price closure', short: 'Economic plausibility', score: 0.22, confidence: 0.92, status: 'clear', finding: 'Scrap unit price is close to the synthetic market benchmark.', metricLabel: 'Price multiple', metricValue: '1.1×', evidence: ['Synthetic invoice lines', 'Demo HSN benchmark'] },
      { id: 'D2a', name: 'Capacity closure', short: 'Throughput density', score: 0.98, confidence: 0.92, status: 'strong', finding: 'Movement-derived throughput is about 96× the clean district × sector median per square metre.', metricLabel: 'Density multiple', metricValue: '96×', evidence: ['Movement-derived attribution', 'Footprint PC-8882', 'Synthetic district-sector benchmark'] },
      { id: 'D2b', name: 'Physical capacity', short: 'Explainable engineering model', score: 0.00, confidence: 1.00, status: 'blocked', finding: 'Bulk-density and handling constants are not promoted beyond calibration in this demo.', blockedReason: 'unsourced_parameter', metricLabel: 'Safety gate', metricValue: 'Blocked', evidence: ['Invariant I9'] },
      { id: 'D3', name: 'Premises aggregation', short: 'Ground reality', score: 0.72, confidence: 0.90, status: 'flag', finding: 'One registration is not a collision cluster, but the 140 m² footprint and local access strengthen the capacity concern.', metricLabel: 'Footprint', metricValue: '140 m²', evidence: ['Synthetic footprint record', 'OSM-style access class'] },
      { id: 'D4', name: 'Network topology', short: 'Syndicate structure', score: 0.76, confidence: 0.88, status: 'flag', finding: 'Billing velocity is above the synthetic 99th percentile and cash tax is only 1.6% of ITC.', metricLabel: 'Cash / ITC', metricValue: '1.6%', evidence: ['Synthetic return summary', 'Registration-age feature'] },
    ],
    premises: { clusterId: 'PC-8882', entityCount: 1, areaM2: 140, landCover: 'Built-up · mixed use', roadClass: 'Narrow local road', geocode: 'Building centroid', joinStatus: 'Matched', attributedCrore: 27.5, densityMultiple: 96 },
    network: { directSuppliers: 7, suspiciousNodes: 2, originDepth: 1, cashToItc: 0.016, sharedIdentifiers: 1, cycle: false },
    price: { hsn: '7204', commodity: 'Ferrous scrap', multiple: 1.1, benchmark: '₹39/kg median', declared: '₹43/kg' },
    guardrails: commonGuardrails,
  },
  {
    id: 'P5-COLLISION',
    gstin: 'SHELL005SYNTH26',
    company: 'Kite Packaging Network',
    pattern: 'P5 · Footprint collision cluster',
    type: 'positive',
    headline: 'Nine nominal manufacturers, one tiny premises',
    description: 'The strongest signal is aggregation rather than imagery: multiple manufacturers share a small footprint, while shared identifiers corroborate the cluster.',
    amount: '₹31.0 cr', period: 'May–Jul 2026', route: 'Refund-risk sweep', district: 'Ahmedabad, Gujarat', declaredRole: 'Manufacturer cluster',
    tier: 'red_cluster', score: 0.93,
    action: 'Prioritise the shared premises for verification and review the connected registrations as one investigation unit.',
    verdict: 'D3 does not claim that a factory is absent; it claims the aggregate declared activity is implausible for the shared footprint.', runtimeMs: 669,
    detectors: [
      { id: 'D1', name: 'Price closure', short: 'Economic plausibility', score: 0.56, confidence: 0.83, status: 'watch', finding: 'Pricing is elevated but not strong enough to carry the case.', metricLabel: 'Price multiple', metricValue: '2.7×', evidence: ['Synthetic invoice lines'] },
      { id: 'D2a', name: 'Capacity closure', short: 'Throughput density', score: 0.89, confidence: 0.90, status: 'flag', finding: 'Aggregated declared value per square metre is a strong district-sector outlier.', metricLabel: 'Density multiple', metricValue: '48×', evidence: ['Movement-derived attribution', 'Synthetic benchmark'] },
      { id: 'D2b', name: 'Physical capacity', short: 'Explainable engineering model', score: 0.00, confidence: 1.00, status: 'blocked', finding: 'No unsourced physical constants are used.', blockedReason: 'unsourced_parameter', metricLabel: 'Safety gate', metricValue: 'Blocked', evidence: ['Invariant I9'] },
      { id: 'D3', name: 'Premises aggregation', short: 'Ground reality', score: 0.99, confidence: 0.96, status: 'strong', finding: 'Nine manufacturers resolve to 112 m² — approximately one registration per 12.4 m².', metricLabel: 'Entity density', metricValue: '1 / 12.4 m²', evidence: ['Rooftop/building-centroid joins', 'Dissolved premises cluster'] },
      { id: 'D4', name: 'Network topology', short: 'Syndicate structure', score: 0.91, confidence: 0.93, status: 'strong', finding: 'Five shared identifiers connect the nominally separate registrations into one supplier cluster.', metricLabel: 'Shared identifiers', metricValue: '5', evidence: ['Synthetic hashed identifiers', 'Invoice graph'] },
    ],
    premises: { clusterId: 'PC-5505', entityCount: 9, areaM2: 112, landCover: 'Built-up · mixed residential', roadClass: 'Residential lane', geocode: '6 rooftop · 3 building centroid', joinStatus: '9 matched', attributedCrore: 31, densityMultiple: 48 },
    network: { directSuppliers: 9, suspiciousNodes: 9, originDepth: 1, cashToItc: 0.009, sharedIdentifiers: 5, cycle: false },
    price: { hsn: '4819', commodity: 'Paper packaging', multiple: 2.7, benchmark: '₹92/kg median', declared: '₹248/kg' },
    guardrails: commonGuardrails,
  },
  {
    id: 'N1-TRADER',
    gstin: 'CLEAN001SYNTH26',
    company: 'Cedar Merchants',
    pattern: 'N1 · Legitimate trader',
    type: 'hard-negative',
    headline: 'No factory, and that is completely legitimate',
    description: 'A trading company has no manufacturing footprint. The role gate blocks D2 and D3 instead of penalising it for a missing factory.',
    amount: '₹2.8 cr', period: 'Aug 2026', route: 'Routine refund', district: 'Jaipur, Rajasthan', declaredRole: 'Trader · no warehousing',
    tier: 'green', score: 0.11,
    action: 'Proceed normally. Preserve the role-gate decisions in the audit trail.',
    verdict: 'This hard negative exists to prove the system does not turn “no factory” into a fraud accusation.', runtimeMs: 274,
    detectors: [
      { id: 'D1', name: 'Price closure', short: 'Economic plausibility', score: 0.18, confidence: 0.94, status: 'clear', finding: 'Declared unit prices are consistent with the synthetic benchmark.', metricLabel: 'Price multiple', metricValue: '1.0×', evidence: ['Synthetic invoice lines'] },
      { id: 'D2a', name: 'Capacity closure', short: 'Throughput density', score: 0, confidence: 1, status: 'blocked', finding: 'Trader without warehousing is exempt from premises throughput testing.', blockedReason: 'role_gate', metricLabel: 'Applicability', metricValue: 'Role-gated', evidence: ['P1 role classification'] },
      { id: 'D2b', name: 'Physical capacity', short: 'Explainable engineering model', score: 0, confidence: 1, status: 'blocked', finding: 'Not applicable.', blockedReason: 'role_gate', metricLabel: 'Applicability', metricValue: 'Role-gated', evidence: ['P1 role classification'] },
      { id: 'D3', name: 'Premises aggregation', short: 'Ground reality', score: 0, confidence: 1, status: 'blocked', finding: 'No manufacturing-premises requirement is inferred for this entity.', blockedReason: 'role_gate', metricLabel: 'Applicability', metricValue: 'Role-gated', evidence: ['P1 role classification'] },
      { id: 'D4', name: 'Network topology', short: 'Syndicate structure', score: 0.13, confidence: 0.91, status: 'clear', finding: 'No suspicious cycle, identifier collision or weak tax-origin pattern is present.', metricLabel: 'Tax-origin depth', metricValue: '5', evidence: ['Synthetic invoice graph'] },
    ],
    premises: { clusterId: 'N/A', entityCount: 1, areaM2: null, landCover: 'Not evaluated', roadClass: 'Not evaluated', geocode: 'Role-gated', joinStatus: 'Not joined', attributedCrore: null, densityMultiple: null },
    network: { directSuppliers: 8, suspiciousNodes: 0, originDepth: 5, cashToItc: 0.23, sharedIdentifiers: 0, cycle: false },
    price: { hsn: '5208', commodity: 'Cotton fabric', multiple: 1, benchmark: '₹280/kg median', declared: '₹280/kg' },
    guardrails: commonGuardrails,
  },
  {
    id: 'N4-PREMIUM',
    gstin: 'PREMIUM04SYN26',
    company: 'Morrow Silk Studio',
    pattern: 'N4 · Premium-product exporter',
    type: 'hard-negative',
    headline: 'Expensive is not automatically fraudulent',
    description: 'A premium silk exporter has a genuinely high unit value. Its price remains within the wider sector dispersion, and the physical/network evidence is clean.',
    amount: '₹6.9 cr', period: 'Jul–Aug 2026', route: 'Zero-rated export refund', district: 'Bengaluru, Karnataka', declaredRole: 'Manufacturer',
    tier: 'green', score: 0.19,
    action: 'Proceed normally. No detector crosses its adverse threshold.',
    verdict: 'The benchmark is sector-aware and dispersion-aware; “premium” is a designed hard negative, not an exception patched in after the fact.', runtimeMs: 334,
    detectors: [
      { id: 'D1', name: 'Price closure', short: 'Economic plausibility', score: 0.39, confidence: 0.88, status: 'clear', finding: 'The premium unit value is 2.2× the median but remains below the robust log-z flag threshold.', metricLabel: 'Price multiple', metricValue: '2.2×', evidence: ['Synthetic premium HSN benchmark', 'Robust log-dispersion'] },
      { id: 'D2a', name: 'Capacity closure', short: 'Throughput density', score: 0.24, confidence: 0.87, status: 'clear', finding: 'Throughput density is ordinary for the district × sector stratum.', metricLabel: 'Density multiple', metricValue: '1.5×', evidence: ['Movement-derived attribution'] },
      { id: 'D2b', name: 'Physical capacity', short: 'Explainable engineering model', score: 0, confidence: 1, status: 'blocked', finding: 'D2b remains calibration-only until all constants are sourced.', blockedReason: 'unsourced_parameter', metricLabel: 'Safety gate', metricValue: 'Blocked', evidence: ['Invariant I9'] },
      { id: 'D3', name: 'Premises aggregation', short: 'Ground reality', score: 0.14, confidence: 0.94, status: 'clear', finding: 'One manufacturer occupies an adequate 1,850 m² industrial cluster.', metricLabel: 'Entity density', metricValue: '1 / 1,850 m²', evidence: ['Synthetic footprint record'] },
      { id: 'D4', name: 'Network topology', short: 'Syndicate structure', score: 0.11, confidence: 0.91, status: 'clear', finding: 'Normal tax origin, normal billing velocity and no shared-identifier cluster.', metricLabel: 'Cash / ITC', metricValue: '19%', evidence: ['Synthetic return summaries'] },
    ],
    premises: { clusterId: 'PC-1404', entityCount: 1, areaM2: 1850, landCover: 'Industrial built-up', roadClass: 'Primary industrial road', geocode: 'Rooftop', joinStatus: 'Matched', attributedCrore: 6.9, densityMultiple: 1.5 },
    network: { directSuppliers: 10, suspiciousNodes: 0, originDepth: 4, cashToItc: 0.19, sharedIdentifiers: 0, cycle: false },
    price: { hsn: '5007', commodity: 'Silk fabric', multiple: 2.2, benchmark: '₹900/kg median', declared: '₹1,980/kg' },
    guardrails: commonGuardrails,
  },
  {
    id: 'N5-ESTATE',
    gstin: 'ESTATE005SYN26',
    company: 'Aravali Industrial Estate',
    pattern: 'N5 · Legitimate shared estate',
    type: 'hard-negative',
    headline: 'Many registrations can legitimately share one site',
    description: 'The same eleven-entity count as the flagship case is placed on a genuine 12,000 m² industrial cluster. Capacity and entity density both clear.',
    amount: '₹38.0 cr', period: 'Apr–Jun 2026', route: 'Routine sweep', district: 'Gurugram, Haryana', declaredRole: 'Manufacturer cluster',
    tier: 'green', score: 0.21,
    action: 'Proceed normally. Co-location alone is not treated as evidence of fraud.',
    verdict: 'This is the workflow counterfactual: larger premises must never become more suspicious when throughput is held constant.', runtimeMs: 418,
    detectors: [
      { id: 'D1', name: 'Price closure', short: 'Economic plausibility', score: 0.17, confidence: 0.92, status: 'clear', finding: 'Prices remain inside normal benchmark dispersion.', metricLabel: 'Price multiple', metricValue: '1.1×', evidence: ['Synthetic invoice lines'] },
      { id: 'D2a', name: 'Capacity closure', short: 'Throughput density', score: 0.49, confidence: 0.92, status: 'clear', finding: 'Density z-equivalent stays just below the Stage-1 flag boundary; the 12,000 m² site absorbs the throughput plausibly.', metricLabel: 'Density z-equivalent', metricValue: '2.98', evidence: ['Synthetic benchmark', '12,000 m² dissolved cluster'] },
      { id: 'D2b', name: 'Physical capacity', short: 'Explainable engineering model', score: 0, confidence: 1, status: 'blocked', finding: 'D2b remains blocked pending sourced constants.', blockedReason: 'unsourced_parameter', metricLabel: 'Safety gate', metricValue: 'Blocked', evidence: ['Invariant I9'] },
      { id: 'D3', name: 'Premises aggregation', short: 'Ground reality', score: 0.19, confidence: 0.95, status: 'clear', finding: 'Eleven registrations across 12,000 m² is compatible with a shared industrial estate.', metricLabel: 'Entity density', metricValue: '1 / 1,091 m²', evidence: ['Synthetic footprint record'] },
      { id: 'D4', name: 'Network topology', short: 'Syndicate structure', score: 0.16, confidence: 0.90, status: 'clear', finding: 'The entities do not form a closed invoice chain and do not share suspicious identifiers.', metricLabel: 'Shared identifiers', metricValue: '0', evidence: ['Synthetic invoice graph'] },
    ],
    premises: { clusterId: 'PC-12000', entityCount: 11, areaM2: 12000, landCover: 'Industrial built-up', roadClass: 'Truck-capable industrial road', geocode: '11 rooftop', joinStatus: '11 matched', attributedCrore: 38, densityMultiple: 6.3 },
    network: { directSuppliers: 14, suspiciousNodes: 0, originDepth: 4, cashToItc: 0.16, sharedIdentifiers: 0, cycle: false },
    price: { hsn: '5407', commodity: 'Synthetic fabric', multiple: 1.1, benchmark: '₹150/kg median', declared: '₹165/kg' },
    guardrails: commonGuardrails,
  },
  {
    id: 'N6-UNRES',
    gstin: 'UNRES006SYNTH26',
    company: 'Ridge Agro Processing',
    pattern: 'N6 · Unresolvable address',
    type: 'hard-negative',
    headline: 'Bad geocoding becomes a field task, not an accusation',
    description: 'The address resolves only to a locality centroid. Physical detectors are suppressed and the case is routed for address verification instead.',
    amount: '₹3.6 cr', period: 'Aug 2026', route: 'Inverted-duty refund', district: 'Nashik, Maharashtra', declaredRole: 'Manufacturer',
    tier: 'amber', score: 0.34,
    action: 'Verify the address on the ground. Do not use physical evidence until geocode confidence improves.',
    verdict: 'The low-confidence geocode is the reason to investigate the address, not evidence that the taxpayer is fraudulent.', runtimeMs: 247,
    detectors: [
      { id: 'D1', name: 'Price closure', short: 'Economic plausibility', score: 0.22, confidence: 0.89, status: 'clear', finding: 'Commodity pricing is ordinary.', metricLabel: 'Price multiple', metricValue: '1.0×', evidence: ['Synthetic invoice lines'] },
      { id: 'D2a', name: 'Capacity closure', short: 'Throughput density', score: 0, confidence: 1, status: 'blocked', finding: 'No premises attribution is attempted at locality-centroid confidence.', blockedReason: 'low_geocode_confidence', metricLabel: 'Geocode gate', metricValue: 'Blocked', evidence: ['P3 hard gate', 'Invariant I2'] },
      { id: 'D2b', name: 'Physical capacity', short: 'Explainable engineering model', score: 0, confidence: 1, status: 'blocked', finding: 'No premises-level capacity inference is allowed from this geocode.', blockedReason: 'low_geocode_confidence', metricLabel: 'Geocode gate', metricValue: 'Blocked', evidence: ['P3 hard gate'] },
      { id: 'D3', name: 'Premises aggregation', short: 'Ground reality', score: 0, confidence: 1, status: 'blocked', finding: 'The address is unresolved at the precision required for an adverse physical finding.', blockedReason: 'low_geocode_confidence', metricLabel: 'Geocode gate', metricValue: 'Blocked', evidence: ['P3 hard gate', 'Invariant I2'] },
      { id: 'D4', name: 'Network topology', short: 'Syndicate structure', score: 0.19, confidence: 0.86, status: 'clear', finding: 'No independent network anomaly is present.', metricLabel: 'Tax-origin depth', metricValue: '3', evidence: ['Synthetic invoice graph'] },
    ],
    premises: { clusterId: 'Unresolved', entityCount: 1, areaM2: null, landCover: 'Not evaluated', roadClass: 'Not evaluated', geocode: 'Locality centroid', joinStatus: 'Unresolved', attributedCrore: null, densityMultiple: null },
    network: { directSuppliers: 5, suspiciousNodes: 0, originDepth: 3, cashToItc: 0.14, sharedIdentifiers: 0, cycle: false },
    price: { hsn: '0713', commodity: 'Pulses', multiple: 1, benchmark: '₹90/kg median', declared: '₹90/kg' },
    guardrails: commonGuardrails,
  },
]

export const defaultCase = demoCases[0]
