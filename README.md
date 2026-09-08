# ITC RADAR — PACE Prototype v2

**Evidence-driven GST Input Tax Credit refund risk screening.**  
React + TypeScript frontend · FastAPI backend · deterministic synthetic cases · Render-ready.

> **Prototype scope:** This repository is a synthetic decision-support demonstration. It does **not** contain real taxpayer data, production-calibrated thresholds, or an automated refund-denial mechanism.

## What changed in v2

The original prototype proved the basic D1 Price Closure flow, but the UI was a conventional purple admin dashboard and D2/D3/D4 were mostly placeholder experiences. v2 keeps the same PACE/ITC RADAR idea and deployment shape while rebuilding the product experience around the project’s real differentiator: **turning declarations into a traceable evidence dossier**.

The redesign is inspired by the visual discipline of Granola: warm off-white surfaces, oversized editorial typography, rounded app windows, sparse navigation, soft yellow/green light, and product UI shown as the hero rather than decorative graphics. It does not copy Granola branding or assets.

### v2 interface

- Minimal pill navigation and editorial hero.
- “Declarations → Evidence enhanced” hero preview.
- Full interactive **Evidence Console** instead of a static dashboard.
- Five visible detector states: D1, D2a, D2b, D3 and D4.
- Human-readable findings, confidence, provenance and blocked reasons.
- Interactive price, premises and network evidence views.
- Risk tier and recommended next action kept separate from detector scores.
- Explicit synthetic-data and human-review labeling throughout.
- Responsive mobile/tablet/desktop layout.
- Zero external image/font dependency; visuals are CSS + inline SVG for reliable Render builds.

### Synthetic case library

The UI contains **9 deterministic scenarios** so the demo proves both detection and restraint:

1. `RC-0001` — flagship over-invoicing + shared-premises shell cluster.
2. `P2-OVER` — over-invoicing / price-closure case.
3. `P3-CYCLE` — circular trading / network-topology case.
4. `P4-VOLUME` — volume inflation / throughput-density case.
5. `P5-COLLISION` — footprint-collision shell cluster.
6. `N1-TRADER` — legitimate trader; physical tests are role-gated.
7. `N4-PREMIUM` — legitimate premium-product exporter.
8. `N5-ESTATE` — legitimate shared industrial estate.
9. `N6-UNRES` — unresolved address; adverse physical findings are blocked.

The positive and hard-negative structure follows the supplied workflow specification. `RC-0001` also mirrors its authoritative worked example.

## Detector model represented in the prototype

| Detector | Purpose | v2 demo behavior |
|---|---|---|
| **D1 — Price Closure** | Compare declared unit value with a robust HSN benchmark | Implemented against deterministic **synthetic** benchmark anchors |
| **D2a — Capacity Closure** | Compare attributed throughput density to district × sector benchmark | Implemented for synthetic case inputs with role/geocode/attribution gates |
| **D2b — Physical Capacity** | Storage/handling engineering explanation | Intentionally blocked with `unsourced_parameter` until constants are citable |
| **D3 — Premises Aggregation** | Detect implausible concentration of goods-supplying GSTINs | Implemented for synthetic premises records and safety gates |
| **D4 — Network Topology** | Detect weak tax origin, cycles, velocity and shared IDs | Implemented as transparent named synthetic features |

Fusion is rule-based: a physical signal does not create an adverse tier unless D1 or D4 corroborates it. Low-confidence premises evidence is suppressed rather than silently discarded.

## Repository layout

```text
.
├── backend/
│   └── app/
│       ├── main.py                 # FastAPI v2 endpoints
│       ├── demo_cases.py           # deterministic synthetic cases
│       └── detectors/              # D1, D2a/D2b, D3, D4, fusion
├── frontend/
│   ├── public/pace-icon.svg
│   └── src/
│       ├── App.tsx                 # redesigned product experience
│       ├── index.css               # responsive Granola-inspired visual system
│       ├── api/client.ts
│       ├── components/Icons.tsx
│       └── data/demoCases.ts
├── docs/
│   ├── workflow.md                 # supplied design specification, unmodified
│   ├── ITC_PPT.pdf                 # supplied SIH deck, unmodified
│   └── ANALYSIS.md                 # v2 design/architecture analysis
├── render.yaml
└── docker-compose.yml
```

## Local run

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Useful endpoints:

```text
GET  /health
GET  /api/health-proxy
GET  /api/demo/cases
POST /api/demo/cases/RC-0001/analyze
POST /api/detectors/d1
GET  /docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite serves at `http://localhost:3000` and proxies `/api` to `http://localhost:8000` in development.

For production, set:

```text
VITE_API_URL=https://YOUR-BACKEND.onrender.com/api
```

If it is not set, the code retains the previous deployed backend fallback for compatibility. The Evidence Console also has a local deterministic fallback so the demo remains explorable during a Render backend cold start.

## Build

```bash
cd frontend
npm install
npm run build
```

Vite is configured to emit `frontend/build`, matching `render.yaml`.

Backend syntax / smoke check:

```bash
PYTHONPATH=backend python -c "from app.demo_cases import analyze_demo_case; print(analyze_demo_case('RC-0001')['risk_tier'])"
```

Expected result: `red_cluster`.

## Render deployment

The repository retains the existing multi-service `render.yaml` structure. For the frontend, set `VITE_API_URL` to the deployed backend **including `/api`**. See `DEPLOYMENT_GUIDE.md` for the replacement workflow.

## Integrity and safety choices

- No real GSTIN/taxpayer records in the demo.
- No claim that synthetic benchmark values are current official market statistics.
- D2b cannot emit an adverse finding while its physical constants are unsourced.
- Role gates protect traders/job-workers/service roles from factory assumptions.
- Low-confidence geocodes cannot support adverse physical findings.
- Physical-only evidence cannot independently escalate to Red.
- The product recommends verification/audit; a human officer decides.
- Blocked/suppressed evidence remains visible for auditability.

## Supplied source material

`docs/workflow.md` and `docs/ITC_PPT.pdf` are included unchanged so the code, prototype and SIH presentation stay in one handoff package.
