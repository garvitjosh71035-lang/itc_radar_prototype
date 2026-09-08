"""ITC Radar / PACE synthetic prototype API.

The API keeps the original D1 endpoint for backwards compatibility and adds a
deterministic case library used by the redesigned React interface. It is a demo
and decision-support prototype, not an automated GST adjudication service.
"""

from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.detectors.d1_price import PriceClosureDetector
from app.demo_cases import DEMO_CASES, analyze_demo_case

settings = get_settings()

app = FastAPI(
    title="ITC Radar — PACE API",
    description="Synthetic evidence-driven GST ITC refund risk detection prototype",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    print("Starting ITC Radar / PACE API v2.0.0")
    print(f"Environment: {settings.ENVIRONMENT}")
    print("Prototype mode: synthetic data only")


@app.get("/")
def root():
    return {
        "service": "ITC Radar — PACE API",
        "version": "2.0.0",
        "mode": "synthetic_demo",
        "endpoints": ["/health", "/api/health-proxy", "/api/detectors/d1", "/api/demo/cases", "/api/demo/cases/{case_id}/analyze", "/docs"],
    }


@app.get("/health")
def health_check():
    # The interactive demo does not require Postgres. This makes Render cold starts
    # and frontend demos independent of optional database availability.
    return {
        "status": "healthy",
        "service": "itc-radar-pace",
        "version": "2.0.0",
        "mode": "synthetic_demo",
        "database_required_for_demo": False,
    }


@app.get("/api/health-proxy")
def api_health_check():
    return health_check()


@app.post("/api/detectors/d1")
def run_d1_price_closure(invoice_lines: List[Dict[str, Any]]):
    try:
        detector = PriceClosureDetector(settings)
        findings = detector.detect(invoice_lines)
        return {
            "detector": "D1",
            "name": "Price Closure",
            "synthetic_benchmark": True,
            "findings_count": len(findings),
            "findings": [f.to_dict() for f in findings],
            "thresholds": {"flag": settings.D1_PRICE_THRESHOLD_FLAG, "strong": settings.D1_PRICE_THRESHOLD_STRONG},
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/demo/cases")
def list_demo_cases():
    return {
        "synthetic": True,
        "count": len(DEMO_CASES),
        "cases": [
            {
                "case_id": case_id,
                "company": case["company"],
                "gstin": case["gstin"],
                "claim_amount_crore": case["claim_amount_crore"],
            }
            for case_id, case in DEMO_CASES.items()
        ],
    }


@app.post("/api/demo/cases/{case_id}/analyze")
def run_demo_case(case_id: str):
    try:
        return analyze_demo_case(case_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown synthetic case: {case_id}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Synthetic analysis failed: {exc}") from exc


@app.post("/api/cases/analyze")
def analyze_case_compat(data: Dict[str, Any]):
    """Backwards-compatible endpoint used by the v1 frontend.

    Pass demo_case_id to run the full deterministic synthetic case. Without it,
    the endpoint runs D1 only and never manufactures D2-D4 evidence.
    """
    demo_case_id = data.get("demo_case_id")
    if demo_case_id:
        try:
            return analyze_demo_case(str(demo_case_id))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Unknown synthetic case: {demo_case_id}") from exc

    gstin = data.get("gstin")
    claim_id = data.get("claim_id")
    if not gstin or not claim_id:
        raise HTTPException(status_code=400, detail="Missing required fields: gstin, claim_id")

    d1 = PriceClosureDetector(settings).detect(data.get("invoice_lines", []))
    return {
        "case_id": claim_id,
        "gstin": gstin,
        "synthetic": True,
        "risk_tier": "amber" if d1 else "green",
        "detectors": {"d1_price": {"findings_count": len(d1), "findings": [f.to_dict() for f in d1]}},
        "notice": "Generic compatibility mode runs D1 only; no physical/network evidence is invented.",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=settings.DEBUG)
