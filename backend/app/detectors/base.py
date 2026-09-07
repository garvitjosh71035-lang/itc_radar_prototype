"""
Base detector class implementing common interface.
All detectors inherit from this and implement the detect() method.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class DetectionTier(Enum):
    """Decision tiers per Section 8.3 of workflow.md"""
    GREEN = "green"      # Normal processing
    AMBER = "amber"      # Post-disbursement audit
    RED = "red"          # Physical verification required
    RED_CLUSTER = "red_cluster"  # Credit blocking consideration


@dataclass
class Finding:
    """
    Standardized finding output matching Section 15.9 schema.
    
    Fields:
    - detector: Which detector produced this (D1-D4)
    - score: Detection score [0, 1]
    - confidence: Confidence level [0, 1]
    - finding_text: Human-readable explanation for officer
    - evidence_refs: Pointers to source records/datasets
    - blocked_reason: Why finding was suppressed (nullable)
    """
    detector: str
    score: float
    confidence: float
    finding_text: str
    evidence_refs: List[str]
    blocked_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "detector": self.detector,
            "score": round(self.score, 4),
            "confidence": round(self.confidence, 4),
            "finding_text": self.finding_text,
            "evidence_refs": self.evidence_refs,
            "blocked_reason": self.blocked_reason,
        }


class BaseDetector(ABC):
    """
    Abstract base class for all detectors.
    
    Implements common interfaces defined in workflow.md Section 5.
    Each detector subclass must implement detect() with appropriate inputs.
    """
    
    NAME: str = NotImplemented  # Class-level constant
    DESCRIPTION: str = NotImplemented
    
    def __init__(self, settings):
        """
        Initialize detector with configuration.
        
        Args:
            settings: Configuration object from app.config.get_settings()
        """
        self.settings = settings
        self._cache: Dict[str, Any] = {}
    
    @abstractmethod
    def detect(self, **kwargs) -> List[Finding]:
        """
        Run detection on input data.
        
        Must be implemented by each detector subclass.
        
        Args:
            kwargs: Detector-specific input data
            
        Returns:
            List of Finding objects
        """
        pass
    
    def _compute_log_z_score(self, value: float, median: float, mad_scale: float) -> float:
        """
        Compute robust log z-score per workflow.md Section 5.
        
        Formula: z = (ln(value) - ln(median)) / (1.4826 × MAD)
        
        This is used by D1 (Price Closure) and D2a (Capacity Closure).
        
        Args:
            value: Declared value being tested
            median: Benchmark median for comparison
            mad_scale: Median Absolute Deviation scaled by 1.4826
            
        Returns:
            z-score as float
        """
        import math
        
        if value <= 0 or median <= 0 or mad_scale <= 0:
            return 0.0
        
        log_ratio = math.log(value / median)
        z_score = log_ratio / mad_scale
        
        return z_score
    
    def _normalize_score(self, z_score: float) -> float:
        """
        Normalize z-score to [0, 1] range.
        
        Uses sigmoid-like transformation for smooth scoring.
        
        Args:
            z_score: Raw z-score (can be negative)
            
        Returns:
            Normalized score in [0, 1]
        """
        import math
        
        # Clamp extreme values
        z_clamped = max(-10, min(10, z_score))
        
        # Sigmoid-like transformation
        score = 1.0 / (1.0 + math.exp(-z_clamped * 2))
        
        return score
    
    def _format_finding_multiple(self, ratio: float) -> str:
        """
        Format finding as plain multiple rather than z-score.
        
        Per workflow.md: "Report the multiple. Never the z-score."
        Example: "declared at 21× the median Indian export price"
        
        Args:
            ratio: Ratio between declared and benchmark value
            
        Returns:
            Human-readable text string
        """
        if ratio >= 1000:
            return f"declared at {ratio:.0f}K× the benchmark"
        elif ratio >= 100:
            return f"declared at {ratio/100:.1f}×100 the benchmark"
        else:
            return f"declared at {ratio:.1f}× the benchmark"
    
    def clear_cache(self):
        """Clear any cached data between runs."""
        self._cache.clear()
    
    def validate_inputs(self, **kwargs) -> bool:
        """
        Validate detector inputs before running detection.
        
        Override in subclasses as needed.
        
        Returns:
            True if inputs are valid, False otherwise
        """
        return True
