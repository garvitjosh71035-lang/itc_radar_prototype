"""D4 — explainable network topology detector for synthetic case graphs."""

from typing import List
from app.detectors.base import BaseDetector, Finding


class NetworkTopologyDetector(BaseDetector):
    NAME = "D4"
    DESCRIPTION = "Network Topology - named syndicate and weak-tax-origin patterns"

    def detect(
        self,
        cash_to_itc_ratio: float | None = None,
        tax_origin_depth: int | None = None,
        velocity_percentile: float | None = None,
        shared_identifier_count: int = 0,
        cycle_detected: bool = False,
        new_entity_cluster: bool = False,
        evidence_refs: list[str] | None = None,
        **_: object,
    ) -> List[Finding]:
        refs = evidence_refs or ["Synthetic depth-3 invoice graph", "Synthetic return summaries"]
        signals: list[str] = []
        score = 0.0

        if cash_to_itc_ratio is not None and cash_to_itc_ratio < self.settings.D4_CASH_TO_ITC_RATIO_THRESHOLD:
            score += 0.28
            signals.append(f"cash-to-ITC {cash_to_itc_ratio * 100:.1f}%")
        if tax_origin_depth is not None and tax_origin_depth <= 1:
            score += 0.26
            signals.append(f"tax-origin depth {tax_origin_depth}")
        if velocity_percentile is not None and velocity_percentile >= 0.99:
            score += 0.18
            signals.append("billing velocity above 99th percentile")
        if shared_identifier_count >= 2:
            score += min(0.22, 0.08 + shared_identifier_count * 0.03)
            signals.append(f"{shared_identifier_count} shared identifiers")
        if cycle_detected:
            score += 0.34
            signals.append("closed invoice cycle")
        if new_entity_cluster:
            score += 0.12
            signals.append("new-registration cluster")

        score = min(0.99, score)
        if score < 0.5:
            return []

        confidence = min(0.97, 0.75 + score * 0.2)
        text = "Named network pattern: " + "; ".join(signals) + "."
        return [Finding(self.NAME, score, confidence, text, refs)]
