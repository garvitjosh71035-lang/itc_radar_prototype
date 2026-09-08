"""D2a — empirical capacity closure for the synthetic prototype.

This implementation intentionally stops at D2a. D2b remains blocked until sector
capacity constants have citable sources, matching workflow invariant I9.
"""

from typing import List
from app.detectors.base import BaseDetector, Finding


PHYSICAL_ROLES = {"manufacturer", "warehouse", "mixed"}
ADVERSE_GEOCODES = {"rooftop", "building_centroid"}


class CapacityClosureDetector(BaseDetector):
    NAME = "D2a"
    DESCRIPTION = "Capacity Closure - empirical throughput density"

    def detect(
        self,
        area_m2: float | None = None,
        attributed_value_crore: float | None = None,
        benchmark_median: float | None = None,
        benchmark_dispersion: float | None = None,
        attribution_confidence: str = "high",
        geocode_tier: str = "rooftop",
        declared_role: str = "manufacturer",
        evidence_refs: list[str] | None = None,
        **_: object,
    ) -> List[Finding]:
        refs = evidence_refs or ["Synthetic premises cluster", "Synthetic district × sector benchmark"]

        if declared_role not in PHYSICAL_ROLES:
            return [Finding(self.NAME, 0.0, 1.0, "Physical throughput test suppressed by the declared-role applicability gate.", refs, "role_gate")]
        if geocode_tier not in ADVERSE_GEOCODES:
            return [Finding(self.NAME, 0.0, 1.0, "Physical throughput test suppressed because the premises geocode is below building-centroid confidence.", refs, "low_geocode_confidence")]
        if attribution_confidence != "high":
            return [Finding(self.NAME, 0.0, 1.0, "Throughput density is retained for prioritisation only because attribution confidence is not high.", refs, "low_attribution_confidence")]
        if not area_m2 or not attributed_value_crore or not benchmark_median or not benchmark_dispersion:
            return []

        density = attributed_value_crore / area_m2
        z_score = self._compute_log_z_score(density, benchmark_median, benchmark_dispersion)
        threshold = self.settings.D2A_DENSITY_THRESHOLD_FLAG
        strong = self.settings.D2A_DENSITY_THRESHOLD_STRONG
        multiple = density / benchmark_median

        if z_score < threshold:
            return []

        severity = "strong flag" if z_score >= strong else "flag"
        confidence = min(0.98, 0.72 + max(0.0, z_score - threshold) * 0.045)
        text = f"Declared throughput density is approximately {multiple:.0f}× the synthetic district-and-sector median — {severity}."
        return [Finding(self.NAME, self._normalize_score(z_score), confidence, text, refs)]


class PhysicalCapacityExplainer(BaseDetector):
    """D2b safety placeholder. It is deliberately non-adverse in this prototype."""

    NAME = "D2b"
    DESCRIPTION = "Physical Capacity - calibration-only explanatory model"

    def detect(self, evidence_refs: list[str] | None = None, **_: object) -> List[Finding]:
        return [Finding(
            self.NAME,
            0.0,
            1.0,
            "No D2b finding emitted because sector physical-capacity parameters have not been sourced to citable standards.",
            evidence_refs or ["Capacity parameter table: calibration pending", "Invariant I9"],
            "unsourced_parameter",
        )]
