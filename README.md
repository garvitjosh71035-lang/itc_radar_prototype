# PACE - Physical Plausibility Engine for GST ITC Refund Adjudication

**Premises-Aggregated Capacity Evidence**

A system to detect fraudulent GST Input Tax Credit refund claims using open earth-observation data, trade statistics, and network analysis.

---

## 🎯 What This System Does

Fraudsters can forge every document in a refund claim. They **cannot** forge:
1. The size of the building they registered
2. The market price of the goods (set by real trade)
3. The fact that nobody upstream ever paid tax in cash

PACE measures these three things from independent open data and flags physically implausible declarations.

**Key innovation:** Dual-constraint closure—raising declared prices hits market benchmarks; raising quantities hits physical capacity limits. No common region where large-scale fraud is feasible.

---

## 📋 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Git repository pushed to GitHub (for Render deployment)

### Run Locally (Development)

```bash
# Clone the repository
git clone <your-repo-url>
cd pace-prototype

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Database: localhost:5432 (password: pace_password)
```

### Deploy to Render.com (Production)

1. Create database on Render:
   - Go to https://dashboard.render.com/

2. Connect your GitHub repo and follow [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 🏥 Health Monitoring System

**New!** Complete health monitoring that checks your services every 5 minutes.

### Quick Start

Run a single test check:
```bash
python scripts/health_monitor.py
```

Start continuous monitoring in production:
```bash
# Windows
scripts\health_monitor.bat

# Or directly:
python scripts/health_monitor.py --daemon
```

### Features

✅ Automated health checks (every 5 minutes)  
✅ Uptime tracking and statistics  
✅ Slack/Email alerts for downtime  
✅ Response time metrics (min/max/avg)  
✅ Beautiful terminal dashboard  
✅ JSON statistics export  
✅ Graceful shutdown handling  

For full documentation, see [scripts/HEALTH_MONITOR_README.md](scripts/HEALTH_MONITOR_README.md)
   - New → PostgreSQL → Use render.yaml config

2. Connect your GitHub repo:
   - New → Web Service → Select repo
   - Build command: `cd backend && pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. Add environment variables from `.env.example`

4. Deploy automatically on git push!

---

## 🏗️ Architecture

### Four Independent Detectors

| Detector | Detects | Data Source | Satellite Needed |
|----------|---------|-------------|------------------|
| **D1 Price Closure** | Over-invoicing (high value, low mass) | UN Comtrade, DGCI&S export stats | ❌ No |
| **D2 Capacity Closure** | Volume inflation (bulk commodities) | Overture Buildings footprints | ✅ Yes |
| **D3 Premises Aggregation** | Shell clusters, ghost suppliers | Overture Buildings, ESA WorldCover | ✅ Yes |
| **D4 Network Topology** | Syndicate structures, circular trading | Invoice graph analysis | ❌ No |

### Pipeline Stages

```
P0 Trigger → P1 Role Gate → P2 Network Assembly → P3 Site Resolution
→ P4 Physical Envelope → P5 Attribution → P6 Detection → P7 Dossier → P8 Feedback
```

### Decision Tiers

- 🟢 **Green**: Normal refund processing
- 🟡 **Amber**: Flagged for post-disbursement audit
- 🔴 **Red**: Physical verification required before disbursement
- 🔴+Cluster: Escalate for Rule 86A credit blocking consideration

---

## 📁 Project Structure

```
pace-prototype/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── detectors/      # D1-D4 implementations
│   │   ├── services/       # Business logic
│   │   ├── routes/         # API endpoints
│   │   ├── models.py       # SQLAlchemy models
│   │   └── main.py         # FastAPI entry point
│   └── Dockerfile
├── frontend/               # React + TypeScript
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── pages/         # Route pages
│   │   └── api/           # API client
│   └── Dockerfile
├── scripts/               # Database initialization & data generation
├── docker-compose.yml     # Local development setup
├── render.yaml            # Render.com deployment config
└── .env.example          # Environment variables template
```

---

## 🗄️ Database Schema (Section 15 of workflow.md)

9 core tables matching the specification:

1. `registration` - GSTIN details, legal name, PAN, constitution
2. `premises` - Registered addresses with geocoding
3. `premises_cluster` - Dissolved building polygons
4. `invoice_line` - Invoice transactions with HSN codes
5. `movement_record` - E-way bill dispatch information
6. `return_summary` - Periodic filing summaries
7. `refund_claim` - Refund applications
8. `attribution` - Throughput assignment to premises
9. `finding` - Detector results with scores and reasons

---

## 🎭 Synthetic Dataset

### Injected Fraud Patterns (Positives)

- **P1**: Pure shell chain (new entities, no cash tax)
- **P2**: Over-invoiced zero-rated supply (21× unit price)
- **P3**: Circular trading (closed loops)
- **P4**: Volume inflation (exceeds physical capacity)
- **P5**: Footprint collision cluster (many firms on tiny footprint)

### Hard Negatives (Legitimate Cases)

- **N1**: Trading company (no factory needed)
- **N2**: Small rural manufacturer (low values, cleared by stratification)
- **N3**: Job-worker (third-party premises)
- **N4**: Premium exporter (genuine high unit price, cleared by corroboration rule)
- **N5**: Shared industrial estate (adequate footprint)
- **N6**: Unresolvable address (field verification routing)

---

## 🔒 Fairness Controls

**Non-negotiable gates protecting honest taxpayers:**

1. ✅ **Role gate**: Traders/job-workers exempted from physical tests
2. ✅ **Geocode confidence gate**: No adverse findings below street-level precision
3. ✅ **Attribution invariant**: Every rupee attributed to exactly ONE premises (no duplication)
4. ✅ **Corroboration rule**: Physical detectors (D2/D3) need paper backing (D1/D4)
5. ✅ **Threshold maturity**: Only S4 thresholds support adverse action; current demo uses S1-S2 for ranking only
6. ✅ **Stratified benchmarking**: District×sector comparisons (protects rural operators)
7. ✅ **Monotonicity**: Larger premises never more suspicious (Invariant I6)

---

## 📊 Key Metrics

- **False-positive rate**: Stratified by urban/rural, turnover band, region
- **Precision@k**: Operational metric (officers work a queue, not threshold)
- **Recall per pattern**: Reported separately for each fraud mode
- **Detector marginal contribution**: Ablation studies showing earth-observation value

---

## 🛠️ Development Workflow

### Run Detectors Individually

```bash
# Test D1 Price Closure
curl http://localhost:8000/api/detectors/d1?gstin=EXP-0001

# Test D3 Premises Aggregation
curl http://localhost:8000/api/detectors/d3?gstin=MAN-0001

# Test full pipeline
curl -X POST http://localhost:8000/api/cases/analyze \
  -H "Content-Type: application/json" \
  -d '{"gstin": "EXP-0001", "claim_id": "RC-001"}'
```

### Generate Synthetic Data

```bash
python scripts/generate_synthetic_data.py --entities 200 --district surat
python scripts/seed_db.py --overwrite
```

### View Evidence Dossier

Frontend URL: `http://localhost:3000/case/{case_id}`
- Overview tab: Entity info, amounts
- Detector Results tab: D1-D4 scores and explanations
- Network Graph tab: Upstream supplier visualization
- Map View tab: Premises cluster overlay
- Evidence Dossier tab: PDF-ready evidence package

---

## 🎯 Demo Day Preparation

### Must-Have Cases

1. **Clear Fraud (Red Tier)**: 8 firms, ₹240 crore, 120 m² footprint
2. **Over-invoicing Only (Amber)**: Single entity, 21× unit price
3. **Hard Negative N4 (Green)**: Premium silk exporter, genuine high price
4. **Industrial Estate (Green)**: Multiple firms, large footprint, plausible density

### Expected Performance

- Frontend load time: <3 seconds
- API response time: <2 seconds per request
- D1 benchmark loading: ~500ms after cache warm-up
- Spatial queries: ~100ms (with PostGIS indexing)

---

## 📚 References

### Statutory
- [Rule 86A CGST Rules](https://cleartax.in/s/all-about-cgst-rule-86a-itc)
- [Notification 04/2024-CT](https://www.gstcouncil.gov.in/sites/default/files/2024-05/04-2024-ct-eng.pdf)
- [CBIC Instruction 03/2025-GST](https://cbic-gst.gov.in/pdf/ins-gst-no-03-2025.pdf)

### Datasets
- [Overture Maps Buildings](https://docs.overturemaps.org/)
- [ESA WorldCover](https://esa-worldcover.org/)
- [UN Comtrade](https://comtradeplus.un.org/)
- [DGCI&S Trade Stats](https://tradestat.commerce.gov.in/)
- [OpenStreetMap India](https://download.geofabrik.de/asia/india.html)

---

## ⚖️ Legal Notice

This system produces evidence only. All adverse decisions require human officer review and written reasoning under Rule 86A. Thresholds here are at Stage S1-S2 maturity—suitable for case prioritization but not yet for adverse action without field validation.

The dossier explicitly documents what the system refused to conclude, ensuring defensible decision-making.

---

## 👥 Team

Built for SIH 2026 as part of the "Fiscal Eye" team.

Based on the technical specification in `workflow.md` and refined through critical analysis in `01_CRITICAL_ANALYSIS.md`.

---

## 📞 Support

Issues and feature requests: Open an issue on this repository.

Technical questions: Refer to the inline code comments and Section 13-19 of workflow.md for normative specifications.

---

**Version**: 1.0.0  
**Status**: MVP Prototype  
**License**: MIT (open source for research and demonstration)
