/**
 * PACE PROTOTYPE - DEMO CASES
 * 
 * This file contains the real-life case examples for demonstration purposes.
 * All data is based on actual GST fraud investigation patterns from FY26.
 */

// ============================================================================
// TYPE DEFINITIONS (Required by App.tsx)
// ============================================================================

export type RiskTier = 'green' | 'amber' | 'red' | 'red_cluster';

export type DetectorId = 'D1' | 'D2a' | 'D2b' | 'D3' | 'D4';

export interface DetectorDemo {
  id: string;
  name: string;
  title: string;
  status: string;
  finding: string;
  confidence: number;
  evidence: string[];
  blockedReason?: string;
}

export interface PremisesData {
  clusterId: string;
  areaM2: number;
  entityCount: number;
}

export interface NetworkData {
  directSuppliers: number;
  originDepth?: number;
  sharedIdentifiers: number;
  cycle: boolean;
  suspiciousNodes: number;
}

export interface DemoCase {
  id: string;
  gstin: string;
  company: string;
  claimAmount: string;
  period: string;
  route: string;
  location: string;
  district: string;
  declaredRole: string;
  riskTier: RiskTier;
  pattern: string;
  headline: string;
  description: string;
  verdict: string;
  action: string;
  score: number;
  runtimeMs: number;
  price: {
    referenceMedian: number;
    declaredValue: number;
    multiple: number;
  };
  premises: PremisesData;
  network: NetworkData;
  detectors: DetectorDemo[];
  guardrails: string[];
  type: 'positive' | 'negative';
}

// ============================================================================
// REAL-LIFE CASE EXAMPLE: OVER-INVOICING FRAUD DETECTION
// ============================================================================

export const rc0001: DemoCase = {
  // BASIC CASE INFO
  id: "RC-0001",
  gstin: "P2OVER0001",
  company: "Aster Exports LLP",
  claimAmount: "₹42.0 cr",
  period: "Apr-Jun 2026",
  route: "Zero-rated export refund",
  location: "Surat, Gujarat",
  district: "Gujarat",
  declaredRole: "Trader · no warehousing",
  riskTier: "red_cluster",
  pattern: "Over-invoicing + shared-premises shell cluster",
  headline: "Export firm declares fabric at 31× market price",
  description: "Aster Exports LLP filed a ₹42 crore export refund claim supported by invoices from suppliers declaring units sold at approximately 31 times the median Indian export unit value for woven fabrics.",
  verdict: "Four independent signals converge. The claimant itself is role-gated from physical tests; the adverse evidence comes from matched upstream manufacturers.",
  action: "Physical verification before disbursement; inspect the supplier cluster and retain drafted reasons for officer review.",
  
  // METRICS
  score: 97,
  runtimeMs: 180,
  
  // PRICE DATA (for D1 detector visualization)
  price: {
    referenceMedian: 150,        // Market rate Rs 150/kg
    declaredValue: 4650,         // Declared Rs 4,650/kg
    multiple: 31                 // Price multiple (31x)
  },
  
  // PREMISES DATA (for D3 detector visualization)
  premises: {
    clusterId: "PC-4471",
    areaM2: 96,                  // 96 m² building footprint
    entityCount: 11              // 11 entities registered there
  },
  
  // NETWORK DATA (for D4 detector visualization)
  network: {
    directSuppliers: 18,
    originDepth: 0,              // No tax-paying upstream suppliers
    sharedIdentifiers: 3,        // 3 shared bank accounts
    cycle: false,                // No circular trading detected
    suspiciousNodes: 11          // 11 flagged suppliers
  },
  
  // GUARDAILS (Fairness Controls)
  guardrails: [
    "Human-in-the-loop decision required",
    "Suppressed findings retained for audit trail",
    "Hard negatives tested in evaluation set"
  ],
  
  // DETECTORS (D1-D4 Pipeline Output)
  detectors: [
    {
      id: "D1",
      name: "Price Closure",
      title: "Economic plausibility",
      status: "Strong flag",
      finding: "Two export lines sit at approximately 28× and 31× the synthetic HSN benchmark median.",
      confidence: 0.96,
      evidence: [
        "DGCI&S trade statistics (Indian exports)",
        "Haven benchmark version: 2026",
        "Unit price calculation: taxable_value / quantity_kg",
        "HSN 5407 median: ₹150/kg",
        "Declared values: ₹4,200/kg and ₹4,650/kg"
      ]
    },
    {
      id: "D2a",
      name: "Capacity Closure",
      title: "Throughput density",
      status: "Strong flag",
      finding: "Aggregate declared throughput density exceeds district-and-sector median by approximately 790 times.",
      confidence: 0.82,
      evidence: [
        "Premises cluster area: 96 m²",
        "Entities registered: 11 suppliers",
        "Total attributed value: ₹380 crore",
        "District × sector benchmark: ₹0.004 crore/m²",
        "Declared density: ₹3.96 crore/m²"
      ]
    },
    {
      id: "D2b",
      name: "Physical Capacity",
      title: "Explainable engineering model",
      status: "Suppressed",
      finding: "No D2b finding emitted because sector physical-capacity parameters have not been sourced to citable standards.",
      confidence: 1.0,
      evidence: [
        "Capacity parameter table: calibration pending",
        "Invariant I9: No adverse finding without citable parameters"
      ],
      blockedReason: "unsourced_parameter"
    },
    {
      id: "D3",
      name: "Premises Aggregation",
      title: "Ground reality",
      status: "Strong flag",
      finding: "11 goods-supplying entities clustered at 1 per 8.7 square meters — far exceeding the threshold of 1 per 50 square meters.",
      confidence: 0.91,
      evidence: [
        "Cluster ID: PC-4471",
        "Building footprint area: 96 m²",
        "Land cover classification: built-up",
        "Road access class: residential",
        "Entity-to-area ratio: 1 per 8.7 m²"
      ]
    },
    {
      id: "D4",
      name: "Network Topology",
      title: "Syndicate structure",
      status: "Strong flag",
      finding: "Tax origin depth 0 for all 11 direct suppliers; cash/ITC ratio of 0.4% across the chain; 3 shared bank account hashes among nominally unrelated entities.",
      confidence: 0.88,
      evidence: [
        "Upstream tax origin depth: 0 (no tax-paying suppliers found)",
        "Cash/ITC ratio: 0.4% (extremely low tax payments)",
        "Shared identifiers: 3 bank accounts used by 11 firms",
        "Registration age at first invoice: all under 90 days old",
        "Billing velocity: 8× above district percentile"
      ]
    }
  ],
  
  // MARKER FOR UI FILTERING
  type: "positive"
};

// ============================================================================
// EXPORT ONLY THIS ONE CASE FOR SIMPLICITY
// ============================================================================
export const demoCases: DemoCase[] = [rc0001];
export const defaultCase = rc0001;
