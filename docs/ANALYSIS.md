# ITC RADAR / PACE — problem, idea and v2 design analysis

## 1. What the project is actually solving

The hard part of fake-ITC/refund fraud is not malformed paperwork. A coordinated fraud network can make registrations, invoices, e-way bills and export/refund documents agree with one another. The project therefore should not present itself as “another GST anomaly dashboard.” Its stronger thesis is that a declaration can be internally consistent yet still fail against evidence the declarant does not control.

PACE organizes that independent evidence into three realities:

- **Market reality:** declared unit price versus an external HSN-level price distribution (D1).
- **Physical reality:** declared activity versus a premises cluster and its usable throughput envelope (D2/D3).
- **Network reality:** invoice graph structure, tax origin, velocity, cycles and shared identifiers (D4).

That is the central product story and the v2 interface makes it visible immediately.

## 2. Why the original visual design undersold the idea

The v1 frontend was functional as a prototype shell, but visually it behaved like a generic risk dashboard:

- purple gradient admin styling;
- large statistic cards before explaining the evidentiary thesis;
- D1 had live behavior while D2/D3/D4 appeared as future features;
- raw JSON was closer to the center of the experience than the officer-facing evidence narrative;
- the UI did not make safety gates, suppressed findings or “why this case clears” equally prominent.

For this project, that is a mismatch. The supplied workflow says the **dossier is the product**. A design should make a judge, mentor, tax officer or hackathon evaluator understand the evidence chain before they care about a model score.

## 3. Product design direction

The visual redesign borrows the *design language*, not the branding, of modern calm productivity products such as Granola:

- warm paper background instead of cyber-security black/purple;
- one strong editorial headline;
- very sparse navigation;
- rounded white application surfaces;
- soft chartreuse/yellow/mint ambient gradients;
- subtle borders and tiny operational metadata;
- the actual product interface shown as the main visual;
- very limited decorative iconography;
- human language first, metrics second.

The result is meant to feel like an evidence notebook for an officer rather than a “fraud AI control room.” That tone better supports a system whose job is to surface evidence and preserve due process.

## 4. New information architecture

### Hero

“Find the fraud the paperwork can’t hide.” immediately explains the asymmetry. A split product preview contrasts a clean-looking declaration with independent enhanced evidence.

### Evidence Console

The primary app view follows this order:

1. **Case context** — who/what/period/refund route.
2. **Decision tier** — Green/Amber/Red/Red + cluster.
3. **Recommended next action** — operational outcome, not an auto-denial.
4. **Detector strip** — D1, D2a, D2b, D3, D4 with clear/flag/strong/blocked states.
5. **Selected evidence** — human-readable finding and source references.
6. **Visual evidence** — unit price position, premises aggregation, network subgraph.
7. **Evidence ledger** — safety gates and provenance.

This makes the UI mirror P0→P7 conceptually without forcing judges to read a pipeline diagram first.

## 5. Fraud examples added

A good synthetic demo must show what the system catches *and what it deliberately clears*. v2 therefore includes five suspicious cases and four restraint cases.

Suspicious cases exercise:

- combined over-invoicing + shell premises;
- pure price anomaly;
- circular trading;
- bulk volume/capacity anomaly;
- multiple manufacturers colliding on one small footprint.

Hard negatives exercise:

- trader with no factory;
- legitimate premium product;
- legitimate multi-registration industrial estate;
- unresolved address.

The clear cases are not filler. They are a direct demonstration that the model is not “suspicion by absence.”

## 6. Backend integrity changes

The rebuilt FastAPI demo removes a duplicate analysis route from v1 and adds deterministic endpoints for the same synthetic case library used by the frontend.

D1, D2a, D3 and D4 return named, explainable findings. D2b remains intentionally blocked. Fusion remains rule-based because the workflow requires explainable corroboration rather than a black-box learned decision.

The generic backwards-compatible analysis endpoint does **not** invent missing physical/network evidence. Without a named demo case it runs D1 only.

## 7. What this prototype still does not claim

- It does not prove national production readiness.
- It does not use confidential GST transaction data.
- It does not present synthetic thresholds as validated field thresholds.
- It does not claim Sentinel imagery can identify every small premises.
- It does not treat a missing factory as proof of fraud.
- It does not automate an adverse financial action.

Those limitations make the demo more credible, not less.

## 8. Best SIH demo path

A strong 3–4 minute walkthrough is:

1. Hero thesis: documents can agree while reality does not.
2. Open `RC-0001` and run it.
3. Click D1 → show 31× price evidence.
4. Click D3 → show 11 registrations on 96 m².
5. Click D4 → show weak tax origin/shared identifiers.
6. Point out D2b is blocked because its constants are not sourced.
7. Switch to `N5-ESTATE`: same idea of co-location, but 12,000 m² clears.
8. Switch to `N1-TRADER`: no factory is okay because role gating blocks physical tests.
9. Finish on “human-reviewed, evidence-led.”

That sequence proves both detection strength and false-positive discipline.
