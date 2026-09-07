"""
Application configuration loaded from environment variables.
Implements Section 16 Stage-1 anchors from workflow.md.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with defaults from .env.example"""
    
    # Environment
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://pace_user:pace_password@localhost:5432/pace_db"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Data Sources
    OVERTURE_MAPS_VERSION: str = "2026-08-19.0"
    DGCI_S_DATA_PATH: str = "./data/dgci_trade_stats.csv"
    
    # ========================================================================
    # DETECTOR THRESHOLDS - Stage-1 Anchors (Section 16.4 of workflow.md)
    # These are starting points for S1-S2 thresholds
    # ========================================================================
    
    # D1 - Price Closure
    D1_PRICE_THRESHOLD_FLAG: float = 3.5       # Flag z-score threshold
    D1_PRICE_THRESHOLD_STRONG: float = 5.0     # Strong flag threshold
    
    # D2a - Capacity Closure
    D2A_DENSITY_THRESHOLD_FLAG: float = 3.0    # Flag z-score threshold
    D2A_DENSITY_THRESHOLD_STRONG: float = 4.5  # Strong flag threshold
    
    # D3 - Premises Aggregation
    # Threshold: >1 GSTIN per 50 m² is suspicious
    D3_ENTITY_DENSITY_PER_M2: float = 0.02     # 1/50 = 0.02 GSTINs per m²
    
    # D4 - Network Topology
    D4_CASH_TO_ITC_RATIO_THRESHOLD: float = 0.02  # <2% cash payment
    
    # Geocoding & Spatial Rules (Section 13)
    GEOCODE_JOIN_TOLERANCE_BUILDING: float = 10.0  # meters
    GEOCODE_JOIN_TOLERANCE_STREET: float = 30.0    # meters
    CLUSTER_DISSOLVE_BUFFER: float = 5.0           # meters (Rule 13.1)
    AMBIQUITY_MARGIN_PERCENT: float = 20.0         # percent (Section 13.3)
    
    # N-floors bound for multi-storey premises (Rule 13.4)
    MAX_FLOORS_BOUND: int = 3
    
    # Fraud Prevalence Assumption (Section 16.4)
    ASSUMED_FRAUD_PREVALENCE: float = 0.02         # 2%
    
    # Pipeline Triggers
    TRIGGER_AMOUNT_CRORE: float = 1.0              # ₹1 crore trigger
    
    # Upstream traversal depth (Section 16.4)
    NETWORK_DEPTH: int = 3
    
    # Minimum sample size for HSN benchmark (Section 5, D1 notes)
    MIN_HSN_SAMPLES: int = 200
    
    # Timeout configurations (seconds)
    HTTP_TIMEOUT: float = 30.0
    SPATIAL_QUERY_TIMEOUT: float = 60.0
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings singleton.
    Ensures settings are loaded once and reused across requests.
    """
    return Settings()
