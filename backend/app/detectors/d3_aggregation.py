"""
D3 - Premises Aggregation Detector (Stub implementation)
Future: Implement footprint clustering and entity density calculations
"""

from app.detectors.base import BaseDetector


class PremisesAggregationDetector(BaseDetector):
    """D3 Premises Aggregation - Not yet implemented"""
    
    NAME = "D3"
    DESCRIPTION = "Premises Aggregation - Detects shell clusters"
    
    def __init__(self, settings):
        super().__init__(settings)
    
    def detect(self, **kwargs):
        return []
