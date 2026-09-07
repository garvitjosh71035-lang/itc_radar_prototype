# PACE Prototype - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Clone & Setup (If not already done)

```bash
cd d:\sih\pace-prototype
git init
git add .
git commit -m "Initial prototype"
```

### Step 2: Start Services with Docker

```bash
docker-compose up -d
```

This starts 4 containers:
- ✅ PostgreSQL + PostGIS (localhost:5432)
- ✅ Redis cache (localhost:6379)
- ✅ FastAPI Backend (localhost:8000)
- ✅ React Frontend (localhost:3000)

### Step 3: Generate Synthetic Data

```bash
# Open a new terminal
cd backend
python scripts/generate_synthetic_data.py --entities 200
```

Output:
```
Generating 200 entities:
  - Fraud patterns: 4
  - Hard negatives: 10
  - Clean entities: 186

Exported to data/
  - entities.json: 200 records
  - invoices.json: ~19,200 records
  - refund_claims.json: ~100 records
```

### Step 4: Seed Database

```bash
python scripts/seed_db.py --overwrite
```

Expected output:
```
Seeding database...
Cleared existing data.

Inserting 200 registrations...
  ✓ Inserted 200 registrations

Inserting ~19,200 invoice lines...
  ✓ Inserted 19,200 invoice lines

Inserting ~100 refund claims...
  ✓ Inserted 100 refund claims

✓ Database seeded successfully!
```

### Step 5: Test API

#### Health Check
```bash
curl http://localhost:8000/health
```

Output:
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "development",
  "debug": true
}
```

#### Run D1 Price Closure Detector

Test flagged case (over-invoiced fabric):
```bash
curl -X POST http://localhost:8000/api/detectors/d1 \
  -H "Content-Type: application/json" \
  -d '[{"taxable_value":2394000,"quantity_kg":760,"hsn":"540792"}]'
```

Expected finding:
```json
{
  "detector": "D1",
  "findings_count": 1,
  "findings": [{
    "score": 0.97,
    "confidence": 0.85,
    "finding_text": "Declares 21.0× the median export unit value...",
    "detector": "D1",
    ...
  }]
}
```

Test clean case:
```bash
curl -X POST http://localhost:8000/api/detectors/d1 \
  -H "Content-Type: application/json" \
  -d '[{"taxable_value":280000,"quantity_kg":1000,"hsn":"520831"}]'
```

Expected: No flag (below threshold).

#### Full Case Analysis

```bash
curl -X POST http://localhost:8000/api/cases/analyze \
  -H "Content-Type: application/json" \
  -d '{"gstin":"P2OVER0001","claim_id":"RC-TEST-001","invoice_lines":[{"taxable_value":2394000,"quantity_kg":760,"hsn":"540792"}]}'
```

### Step 6: Access Frontend

Open browser:
- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs

---

## 📋 Complete Workflow

### Full Development Cycle

```bash
# 1. Start all services
docker-compose up -d

# 2. Wait for DB to be ready (usually ~5 seconds)
sleep 5

# 3. Generate synthetic data
cd backend && python scripts/generate_synthetic_data.py --entities 500

# 4. Seed database
python scripts/seed_db.py --overwrite

# 5. Run tests
pytest tests/

# 6. Stop when done
docker-compose down
```

### Production Deployment to Render

```bash
# 1. Push to GitHub
git push origin main

# 2. Go to https://dashboard.render.com/
# 3. New → PostgreSQL (use render.yaml config)
# 4. New → Web Service → Select repo
# 5. Connect environment variables from .env.example
# 6. Auto-deploys on git push!
```

---

## 🎯 Demo Day Cases

### Case 1: Clear Fraud (Red Tier)
Entity: `P2OVER0001`  
Claim: ₹23.94 crore  
Finding: 21× market price (D1 strong flag)

### Case 2: Premium Exporter (Amber/Green)
Entity: `N4PRMI0001`  
Claim: Genuine premium silk at 10× price  
Finding: D1 fires but cleared by corroboration rule (hard negative N4)

### Case 3: Clean Business (Green)
Entity: `CLEAN0001`  
Claim: Normal cotton fabric  
Finding: Below all thresholds, no flags

---

## 🔧 Troubleshooting

### Database Connection Failed
```bash
docker ps  # Check if container is running
docker-compose logs db  # View errors
```

### Port Already in Use
```bash
docker-compose down
docker rm pace-db pace-backend  # Remove stuck containers
docker-compose up -d
```

### Data Not Loading
```bash
cd backend
python scripts/seed_db.py --overwrite
# Ensure JSON files exist first
ls -la ../data/*.json
```

---

## 📊 Expected Performance

| Operation | Time |
|-----------|------|
| Frontend load | < 3s |
| API health check | < 100ms |
| D1 detection (1k invoices) | ~2s |
| Database seeding (500 entities) | ~10s |
| Docker startup | ~20s |

---

## 📈 Next Steps

1. Implement D3 Premises Aggregation detector
2. Add spatial processing services
3. Build full frontend dashboard
4. Add PDF dossier generation
5. Implement D4 Network Topology detector
6. Deploy to Render.com

---

## 🆘 Support

For issues:
1. Check docker-compose logs
2. Verify `.env` file exists
3. Ensure PostgreSQL port 5432 is free
4. Try fresh database seed

Documentation: See `README.md` and `workflow.md`
