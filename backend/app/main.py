"""
PACE - Physical Plausibility Engine for GST ITC Refund Adjudication
FastAPI Application Entry Point

Implements workflow.md Sections 7 (Pipeline Stages) and 15 (Data Dictionary)
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import asyncio

from app.config import get_settings
from app.database import get_db, Base, engine, init_db
from app.models import Registration, InvoiceLine, RefundClaim
from app.detectors.d1_price import PriceClosureDetector


# Initialize FastAPI app
settings = get_settings()

app = FastAPI(
    title="PACE API",
    description="Physical Plausibility Engine for GST ITC Refund Adjudication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# LIFECYCLE
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Initialize database tables on startup.
    Called once when application starts.
    """
    import os
    print(f"Starting PACE Backend v{__import__('app').__version__}")
    print(f"Environment: {settings.ENVIRONMENT}")
    
    # Only create tables if DATABASE_URL is available (not in production initially)
    # In production, tables are created via migration script or manually
    if settings.is_development:
        # Create all SQLAlchemy models in database for development
        try:
            Base.metadata.create_all(bind=engine)
            init_db()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Warning: Database initialization skipped: {e}")


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
def health_check():
    """
    Health check endpoint for deployment validation.
    Returns system status and connected services.
    """
    try:
        from app.database import check_connection
        
        db_status = "connected" if check_connection() else "disconnected"
        
        return {
            "status": "healthy",
            "database": db_status,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


# ============================================================================
# ROOT DETECTOR ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "service": "PACE API",
        "version": "1.0.0",
        "description": "Physical Plausibility Engine for GST ITC Refund Adjudication",
        "endpoints": [
            "/health",
            "/api/detectors/d1",
            "/api/cases/analyze",
            "/docs"
        ],
    }


# ============================================================================
# D1 PRICE CLOSURE DETECTOR ENDPOINT
# ============================================================================

@app.post("/api/detectors/d1")
def run_d1_price_closure(invoice_lines: List[Dict[str, Any]]):
    """
    Run D1 Price Closure Detector on invoice lines.
    
    Input format per Section 15.4:
    {
        "taxable_value": 10000.0,
        "quantity_kg": 10.0,
        "hsn": "540792"
    }
    
    Returns findings where declared price exceeds benchmarks.
    """
    try:
        detector = PriceClosureDetector(settings)
        findings = detector.detect(invoice_lines)
        
        return {
            "detector": "D1",
            "name": "Price Closure",
            "findings_count": len(findings),
            "findings": [f.to_dict() for f in findings],
            "thresholds": {
                "flag": settings.D1_PRICE_THRESHOLD_FLAG,
                "strong": settings.D1_PRICE_THRESHOLD_STRONG,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CASE ANALYSIS ENDPOINT (Placeholder for full pipeline)
# ============================================================================

@app.post("/api/cases/analyze")
def analyze_case(data: Dict[str, Any]):
    """
    Full case analysis pipeline (P0-P8).
    
    Currently implements only D1 + simple mock results.
    Full implementation will be added iteratively.
    
    Input:
    {
        "gstin": "EXP-0001",
        "claim_id": "RC-001",
        "invoice_lines": [...]
    }
    
    Returns:
    {
        "case_id": "CASE-001",
        "risk_tier": "amber",
        "detectors": {...},
        "dossier_url": "/cases/CASE-001/dossier"
    }
    """
    gstin = data.get("gstin")
    claim_id = data.get("claim_id")
    invoice_lines = data.get("invoice_lines", [])
    
    if not gstin:
        raise HTTPException(status_code=400, detail="Missing GSTIN")
    
    if not claim_id:
        raise HTTPException(status_code=400, detail="Missing claim_id")
    
    try:
        # Run D1 detector
        d1_detector = PriceClosureDetector(settings)
        d1_findings = d1_detector.detect(invoice_lines)
        
        # Mock results for other detectors (will be implemented later)
        d3_findings = []
        d4_findings = []
        
        # Determine risk tier based on findings
        has_strong_flag = any(
            f.z_score >= settings.D1_PRICE_THRESHOLD_STRONG 
            for f in d1_findings
        )
        
        risk_tier = "green"
        if has_strong_flag:
            risk_tier = "red" if d3_findings else "amber"
        elif d1_findings:
            risk_tier = "amber"
        
        return {
            "case_id": f"CASE-{gstin}",
            "gstin": gstin,
            "claim_id": claim_id,
            "risk_tier": risk_tier,
            "detectors": {
                "d1_price": {
                    "findings_count": len(d1_findings),
                    "findings": [f.to_dict() for f in d1_findings],
                },
                "d3_aggregation": {
                    "findings_count": len(d3_findings),
                    "findings": [],
                },
                "d4_network": {
                    "findings_count": len(d4_findings),
                    "findings": [],
                },
            },
            "status": "analysis_complete",
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ============================================================================
# SAMPLE DATA ENDPOINTS (For demo purposes)
# ============================================================================

@app.get("/api/sample/invoices/d1-flagged")
def sample_invoice_d1_flagged():
    """
    Sample invoice line that should trigger D1 flag.
    
    Example: Over-invoiced fabric at 21× market price
    """
    return {
        "description": "Over-invoiced synthetic fabric (HSN 5407)",
        "invoice_lines": [
            {
                "taxable_value": 2394000.0,
                "quantity_kg": 760.0,
                "hsn": "540792",
                "unit_price_calculated": 3150.0,
                "benchmark_median": 150.0,
                "multiple": 21.0,
            }
        ]
    }


@app.get("/api/sample/invoices/d1-clean")
def sample_invoice_d1_clean():
    """
    Sample invoice line that should NOT trigger D1 flag.
    
    Example: Normally priced goods
    """
    return {
        "description": "Normally priced cotton fabric (HSN 5208)",
        "invoice_lines": [
            {
                "taxable_value": 280000.0,
                "quantity_kg": 1000.0,
                "hsn": "520831",
                "unit_price_calculated": 280.0,
                "benchmark_median": 280.0,
                "multiple": 1.0,
            }
        ]
    }


# ============================================================================
# DATABASE QUERIES (Basic CRUD for testing)
# ============================================================================

@app.get("/api/registrations")
def list_registrations(db: Session = Depends(get_db)):
    """List all registered entities."""
    registrations = db.query(Registration).limit(100).all()
    
    return {
        "count": len(registrations),
        "registrations": [
            {
                "gstin": r.gstin,
                "legal_name": r.legal_name,
                "status": r.status,
            }
            for r in registrations
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
