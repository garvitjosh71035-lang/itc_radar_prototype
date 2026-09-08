"""Transparent fusion rules from workflow Section 8."""

from app.detectors.base import Finding


class DecisionFusion:
    def fuse_findings(self, findings: list[Finding], network_cluster: bool = False, address_unverifiable: bool = False) -> dict:
        active = [f for f in findings if not f.blocked_reason and f.score >= 0.5]
        ids = {f.detector for f in active}
        physical = bool(ids & {"D2a", "D2b", "D3"})
        corroborator = bool(ids & {"D1", "D4"})

        if physical and corroborator:
            tier = "red_cluster" if network_cluster and "D4" in ids else "red"
        elif active or address_unverifiable:
            tier = "amber"
        else:
            tier = "green"

        # Score is only a presentation aid in the prototype; tier rules remain authoritative.
        score = max([f.score for f in active], default=0.08)
        if tier == "red_cluster":
            score = max(score, 0.93)
        elif tier == "red":
            score = max(score, 0.86)
        elif tier == "amber":
            score = min(max(score, 0.34), 0.79)
        else:
            score = min(score, 0.29)

        return {
            "tier": tier,
            "risk_score": round(score, 4),
            "active_detectors": sorted(ids),
            "suppressed_findings": [f.to_dict() for f in findings if f.blocked_reason],
            "corroboration_satisfied": physical and corroborator,
        }
