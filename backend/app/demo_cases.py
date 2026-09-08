"""Deterministic synthetic cases used by the SIH prototype UI.

No record in this module represents a real taxpayer. The values are constructed to
exercise the positive patterns P1-P5 and hard negatives N1/N4/N5/N6 described in
workflow.md.
"""

from app.config import get_settings
from app.detectors.d1_price import PriceClosureDetector
from app.detectors.d2_capacity import CapacityClosureDetector, PhysicalCapacityExplainer
from app.detectors.d3_aggregation import PremisesAggregationDetector
from app.detectors.d4_network import NetworkTopologyDetector
from app.detectors.fusion import DecisionFusion


DEMO_CASES = {
    "RC-0001": {
        "company": "Aster Exports LLP",
        "gstin": "EXP0001SYNTH26",
        "claim_amount_crore": 42.0,
        "invoice_lines": [
            {"taxable_value": 210_000_000, "quantity_kg": 50_000, "hsn": "5407"},
            {"taxable_value": 186_000_000, "quantity_kg": 40_000, "hsn": "5407"},
        ],
        "capacity": {"area_m2": 96, "attributed_value_crore": 380, "benchmark_median": 0.005, "benchmark_dispersion": 0.62, "attribution_confidence": "high", "geocode_tier": "rooftop", "declared_role": "manufacturer"},
        "premises": {"entity_count": 11, "area_m2": 96, "geocode_tier": "rooftop", "declared_role": "manufacturer", "join_status": "matched", "landcover_class": "built-up residential context", "road_class": "residential lane"},
        "network": {"cash_to_itc_ratio": 0.004, "tax_origin_depth": 0, "velocity_percentile": 0.999, "shared_identifier_count": 3, "cycle_detected": False, "new_entity_cluster": True},
        "network_cluster": True,
    },
    "P2-OVER": {
        "company": "Northstar Trading Co.", "gstin": "OVERINV002SYN26", "claim_amount_crore": 8.4,
        "invoice_lines": [{"taxable_value": 60_000_000, "quantity_kg": 20_000, "hsn": "5407"}],
        "capacity": {"declared_role": "trader"}, "premises": {"declared_role": "trader"},
        "network": {"cash_to_itc_ratio": 0.18, "tax_origin_depth": 4, "velocity_percentile": 0.61, "shared_identifier_count": 0},
        "network_cluster": False,
    },
    "P3-CYCLE": {
        "company": "Orbit Components Pvt. Ltd.", "gstin": "CYCLE003SYNTH26", "claim_amount_crore": 16.2,
        "invoice_lines": [],
        "capacity": {"area_m2": 780, "attributed_value_crore": 16.2, "benchmark_median": 0.01, "benchmark_dispersion": 0.65, "attribution_confidence": "high", "geocode_tier": "rooftop", "declared_role": "manufacturer"},
        "premises": {"entity_count": 1, "area_m2": 780, "geocode_tier": "rooftop", "declared_role": "manufacturer", "join_status": "matched", "landcover_class": "industrial built-up", "road_class": "secondary road"},
        "network": {"cash_to_itc_ratio": 0.015, "tax_origin_depth": 1, "velocity_percentile": 0.92, "shared_identifier_count": 0, "cycle_detected": True},
        "network_cluster": False,
    },
    "P4-VOLUME": {
        "company": "Delta Recyclers", "gstin": "BULK004SYNTH26", "claim_amount_crore": 27.5,
        "invoice_lines": [],
        "capacity": {"area_m2": 140, "attributed_value_crore": 27.5, "benchmark_median": 0.00205, "benchmark_dispersion": 0.55, "attribution_confidence": "high", "geocode_tier": "building_centroid", "declared_role": "manufacturer"},
        "premises": {"entity_count": 1, "area_m2": 140, "geocode_tier": "building_centroid", "declared_role": "manufacturer", "join_status": "matched", "landcover_class": "built-up mixed use", "road_class": "narrow local road"},
        "network": {"cash_to_itc_ratio": 0.016, "tax_origin_depth": 1, "velocity_percentile": 0.995, "shared_identifier_count": 1},
        "network_cluster": False,
    },
    "P5-COLLISION": {
        "company": "Kite Packaging Network", "gstin": "SHELL005SYNTH26", "claim_amount_crore": 31.0,
        "invoice_lines": [],
        "capacity": {"area_m2": 112, "attributed_value_crore": 31, "benchmark_median": 0.00577, "benchmark_dispersion": 0.6, "attribution_confidence": "high", "geocode_tier": "rooftop", "declared_role": "manufacturer"},
        "premises": {"entity_count": 9, "area_m2": 112, "geocode_tier": "rooftop", "declared_role": "manufacturer", "join_status": "matched", "landcover_class": "built-up mixed residential", "road_class": "residential lane"},
        "network": {"cash_to_itc_ratio": 0.009, "tax_origin_depth": 1, "velocity_percentile": 0.997, "shared_identifier_count": 5, "new_entity_cluster": True},
        "network_cluster": True,
    },
    "N1-TRADER": {
        "company": "Cedar Merchants", "gstin": "CLEAN001SYNTH26", "claim_amount_crore": 2.8,
        "invoice_lines": [{"taxable_value": 280_000, "quantity_kg": 1_000, "hsn": "5208"}],
        "capacity": {"declared_role": "trader"}, "premises": {"declared_role": "trader"},
        "network": {"cash_to_itc_ratio": 0.23, "tax_origin_depth": 5, "velocity_percentile": 0.45, "shared_identifier_count": 0},
        "network_cluster": False,
    },
    "N4-PREMIUM": {
        "company": "Morrow Silk Studio", "gstin": "PREMIUM04SYN26", "claim_amount_crore": 6.9,
        "invoice_lines": [{"taxable_value": 19_800_000, "quantity_kg": 10_000, "hsn": "5007"}],
        "capacity": {"area_m2": 1850, "attributed_value_crore": 6.9, "benchmark_median": 0.0025, "benchmark_dispersion": 0.65, "attribution_confidence": "high", "geocode_tier": "rooftop", "declared_role": "manufacturer"},
        "premises": {"entity_count": 1, "area_m2": 1850, "geocode_tier": "rooftop", "declared_role": "manufacturer", "join_status": "matched", "landcover_class": "industrial built-up", "road_class": "industrial road"},
        "network": {"cash_to_itc_ratio": 0.19, "tax_origin_depth": 4, "velocity_percentile": 0.55, "shared_identifier_count": 0},
        "network_cluster": False,
    },
    "N5-ESTATE": {
        "company": "Aravali Industrial Estate", "gstin": "ESTATE005SYN26", "claim_amount_crore": 38.0,
        "invoice_lines": [{"taxable_value": 16_500_000, "quantity_kg": 100_000, "hsn": "5407"}],
        "capacity": {"area_m2": 12_000, "attributed_value_crore": 38, "benchmark_median": 0.0005, "benchmark_dispersion": 0.62, "attribution_confidence": "high", "geocode_tier": "rooftop", "declared_role": "manufacturer"},
        "premises": {"entity_count": 11, "area_m2": 12_000, "geocode_tier": "rooftop", "declared_role": "manufacturer", "join_status": "matched", "landcover_class": "industrial built-up", "road_class": "truck-capable industrial road"},
        "network": {"cash_to_itc_ratio": 0.16, "tax_origin_depth": 4, "velocity_percentile": 0.57, "shared_identifier_count": 0},
        "network_cluster": False,
    },
    "N6-UNRES": {
        "company": "Ridge Agro Processing", "gstin": "UNRES006SYNTH26", "claim_amount_crore": 3.6,
        "invoice_lines": [{"taxable_value": 900_000, "quantity_kg": 10_000, "hsn": "0713"}],
        "capacity": {"area_m2": 450, "attributed_value_crore": 3.6, "benchmark_median": 0.003, "benchmark_dispersion": 0.6, "attribution_confidence": "high", "geocode_tier": "locality_centroid", "declared_role": "manufacturer"},
        "premises": {"entity_count": 1, "area_m2": 450, "geocode_tier": "locality_centroid", "declared_role": "manufacturer", "join_status": "unresolved"},
        "network": {"cash_to_itc_ratio": 0.14, "tax_origin_depth": 3, "velocity_percentile": 0.58, "shared_identifier_count": 0},
        "network_cluster": False, "address_unverifiable": True,
    },
}


def analyze_demo_case(case_id: str) -> dict:
    if case_id not in DEMO_CASES:
        raise KeyError(case_id)

    settings = get_settings()
    case = DEMO_CASES[case_id]
    findings = []

    findings.extend(PriceClosureDetector(settings).detect(case.get("invoice_lines", [])))
    findings.extend(CapacityClosureDetector(settings).detect(**case.get("capacity", {})))
    findings.extend(PhysicalCapacityExplainer(settings).detect())
    findings.extend(PremisesAggregationDetector(settings).detect(**case.get("premises", {})))
    findings.extend(NetworkTopologyDetector(settings).detect(**case.get("network", {})))

    fusion = DecisionFusion().fuse_findings(
        findings,
        network_cluster=case.get("network_cluster", False),
        address_unverifiable=case.get("address_unverifiable", False),
    )

    return {
        "case_id": case_id,
        "gstin": case["gstin"],
        "company": case["company"],
        "synthetic": True,
        "claim_amount_crore": case["claim_amount_crore"],
        "risk_tier": fusion["tier"],
        "risk_score": fusion["risk_score"],
        "corroboration_satisfied": fusion["corroboration_satisfied"],
        "active_detectors": fusion["active_detectors"],
        "findings": [f.to_dict() for f in findings],
        "suppressed_findings": fusion["suppressed_findings"],
        "threshold_stage": "S1 synthetic anchors",
        "notice": "Synthetic demonstration only. No real taxpayer records or production-calibrated thresholds are used.",
    }
