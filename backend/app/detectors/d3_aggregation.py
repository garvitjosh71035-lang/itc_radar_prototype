"""D3 — premises aggregation detector for synthetic / demo records."""

from typing import List
from app.detectors.base import BaseDetector, Finding

PHYSICAL_ROLES = {"manufacturer", "warehouse", "mixed"}
ADVERSE_GEOCODES = {"rooftop", "building_centroid"}


class PremisesAggregationDetector(BaseDetector):
    NAME = "D3"
    DESCRIPTION = "Premises Aggregation - detects implausible registration concentration"

    def detect(
        self,
        entity_count: int = 0,
        area_m2: float | None = None,
        geocode_tier: str = "rooftop",
        declared_role: str = "manufacturer",
        join_status: str = "matched",
        landcover_class: str | None = None,
        road_class: str | None = None,
        evidence_refs: list[str] | None = None,
        **_: object,
    ) -> List[Finding]:
        refs = evidence_refs or ["Synthetic dissolved building cluster", "Synthetic geocode record"]

        if declared_role not in PHYSICAL_ROLES:
            return [Finding(self.NAME, 0.0, 1.0, "Premises aggregation suppressed by the declared-role applicability gate.", refs, "role_gate")]
        if geocode_tier not in ADVERSE_GEOCODES or join_status != "matched":
            return [Finding(self.NAME, 0.0, 1.0, "Premises aggregation suppressed because the site resolution is not precise enough for an adverse finding.", refs, "low_geocode_confidence")]
        if not area_m2 or entity_count <= 0:
            return []

        density = entity_count / area_m2
        threshold = self.settings.D3_ENTITY_DENSITY_PER_M2
        if density <= threshold:
            return []

        ratio = density / threshold
        score = min(0.99, 0.62 + ratio * 0.08)
        confidence = 0.94 if geocode_tier == "rooftop" else 0.88
        context = []
        if landcover_class:
            context.append(landcover_class)
        if road_class:
            context.append(road_class)
        suffix = f" Context: {', '.join(context)}." if context else ""
        text = f"{entity_count} goods-supplying registrations resolve to {area_m2:,.0f} m² — approximately one entity per {area_m2 / entity_count:.1f} m².{suffix}"
        return [Finding(self.NAME, score, confidence, text, refs)]
