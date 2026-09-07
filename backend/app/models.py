"""
Database models implementing Section 15 of workflow.md.
9 core tables matching the specification exactly.
"""

from datetime import date, datetime
from typing import Optional
from uuid import uuid4, UUID
from sqlalchemy import (
    Column, String, Date, Numeric, Boolean, Integer,
    Text, ForeignKey, CheckConstraint, Index, DateTime, func
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from app.database import Base


# =============================================================================
# ENUMS (Section 15)
# =============================================================================

class Constitution(str):
    PROPRIETORSHIP = "proprietorship"
    PARTNERSHIP = "partnership"
    LLP = "llp"
    PRIVATE_LIMITED = "private_ltd"
    PUBLIC_LIMITED = "public_ltd"
    HUF = "huf"
    TRUST = "trust"
    OTHER = "other"


class RegistrationStatus(str):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    PROVISIONAL = "provisional"


class DeclaredRole(str):
    MANUFACTURER = "manufacturer"
    TRADER = "trader"
    WAREHOUSE = "warehouse"
    JOB_WORKER = "job_worker"
    SERVICE = "service"
    MIXED = "mixed"


class PremisesType(str):
    PRINCIPAL = "principal"
    ADDITIONAL = "additional"


class GeocodeTier(str):
    ROOFTOP = "rooftop"
    BUILDING_CENTROID = "building_centroid"
    STREET = "street"
    LOCALITY_CENTROID = "locality_centroid"
    UNRESOLVED = "unresolved"


class JoinStatus(str):
    MATCHED = "matched"
    CANDIDATE = "candidate"
    AMBIGUOUS = "ambiguous"
    UNRESOLVED = "unresolved"
    NO_STRUCTURE = "no_structure"


class SupplyType(str):
    DOMESTIC = "domestic"
    EXPORT = "export"
    SEZ_SUPPLY = "sez_supply"
    DEEMED_EXPORT = "deemed_export"


class RefundRoute(str):
    ZERO_RATED_EXPORT = "zero_rated_export"
    SEZ_SUPPLY = "sez_supply"
    INVERTED_DUTY = "inverted_duty"
    OTHER = "other"


class AttributionMethod(str):
    MOVEMENT_DERIVED = "movement_derived"
    EVEN_SPLIT = "even_split"
    PRINCIPAL_ONLY = "principal_only"


class AttributionConfidence(str):
    HIGH = "high"
    LOW = "low"


class DetectorName(str):
    D1 = "D1"       # Price Closure
    D2A = "D2a"     # Capacity Closure (empirical)
    D2B = "D2b"     # Capacity Closure (physical model)
    D3 = "D3"       # Premises Aggregation
    D4 = "D4"       # Network Topology


class BlockedReason(str):
    LOW_GEOCODE_CONFIDENCE = "low_geocode_confidence"
    ROLE_GATE = "role_gate"
    UNSOURCED_PARAMETER = "unsourced_parameter"
    LOW_ATTRIBUTION_CONFIDENCE = "low_attribution_confidence"
    AMBIGUOUS_JOIN = "ambiguous_join"


# =============================================================================
# TABLE 1: REGISTRATION
# =============================================================================

class Registration(Base):
    """
    Table: registration (Section 15.1)
    
    Fields:
    - gstin: Primary key, checksum-valid format (15 chars)
    - legal_name: As registered with GST authority
    - pan: Derivable from GSTIN positions 3-12, used for clustering
    - constitution: Business structure type
    - registration_date: When entity was registered
    - status: Current registration status
    - declared_role: Manufacturer/trader/etc (for P1 role gate)
    - declared_hsn: Array of HSN codes involved in business
    - authorised_signatory_id: Hashed identity token (not raw PII)
    - bank_account_hash: Hashed bank accounts (for D4 shared-identifier)
    - contact_hash: Hashed mobile/email (for D4 clustering)
    """
    __tablename__ = "registration"
    
    gstin = Column(String(15), primary_key=True, nullable=False)
    legal_name = Column(Text, nullable=False)
    pan = Column(String(10), nullable=False, index=True)
    constitution = Column(String(50), nullable=False)
    registration_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False, default='active')
    cancellation_date = Column(Date, nullable=True)
    declared_role = Column(String(50), nullable=True)
    declared_hsn = Column(ARRAY(String(8)), nullable=False)
    authorised_signatory_id = Column(Text, nullable=True)
    bank_account_hash = Column(ARRAY(String), nullable=True)
    contact_hash = Column(ARRAY(String), nullable=True)
    
    # Relationships
    premises = relationship("Premises", back_populates="registration")
    refund_claims = relationship("RefundClaim", back_populates="registration")
    
    __table_args__ = (
        CheckConstraint("length(gstin) = 15", name="check_gstin_length"),
    )


# =============================================================================
# TABLE 2: PREMISES
# =============================================================================

class Premises(Base):
    """
    Table: premises (Section 15.2)
    
    Fields:
    - premises_id: UUID primary key
    - gstin: Foreign key to registration
    - premises_type: Principal or additional place of business
    - address_raw: Original declared address string
    - geom: Geocoded point coordinates (EPSG:4326)
    - geocode_tier: Precision level of geocoding
    - geocode_source: Where coordinates came from
    - cluster_id: FK to premises_cluster (null if not matched)
    - join_status: Result of geocode-to-cluster join
    - goods_capable: Can this premises receive throughput attribution?
    """
    __tablename__ = "premises"
    
    premises_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    gstin = Column(String(15), ForeignKey("registration.gstin"), nullable=False)
    premises_type = Column(String(50), nullable=False)
    address_raw = Column(Text, nullable=False)
    geom = Column(Geometry("POINT", srid=4326), nullable=True)
    geocode_tier = Column(String(50), nullable=False)
    geocode_source = Column(Text, nullable=False)
    cluster_id = Column(PGUUID(as_uuid=True), nullable=True)
    join_status = Column(String(50), nullable=False)
    goods_capable = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    registration = relationship("Registration", back_populates="premises")
    movement_records = relationship("MovementRecord", back_populates="origin_premises")
    attributions = relationship("Attribution", back_populates="premises")
    
    __table_args__ = (
        Index("idx_premises_geom", geom, postgresql_using="gist"),
    )


# =============================================================================
# TABLE 3: PREMISES_CLUSTER
# =============================================================================

class PremisesCluster(Base):
    """
    Table: premises_cluster (Section 15.3)
    
    Dissolved union of building polygons within buffer distance (Rule 13.1).
    Unit of analysis for D2a and D3 detectors.
    
    Fields:
    - cluster_id: UUID primary key
    - geom: Multipolygon geometry (dissolved per Rule 13.1)
    - area_m2: Geodesic area in square meters (computed on ellipsoid)
    - polygon_count: Number of source polygons dissolved
    - n_floors_bound: Default 3 per Rule 13.4
    - landcover_class: ESA WorldCover class at centroid
    - access_road_class: OSM highway tag of nearest road
    - access_road_width_m: Road width if tagged
    - district_code: Stratification key
    - source_dataset_version: Overture release version for provenance
    """
    __tablename__ = "premises_cluster"
    
    cluster_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    geom = Column(Geometry("MULTIPOLYGON", srid=4326), nullable=False, unique=True)
    area_m2 = Column(Numeric(12, 2), nullable=False)
    polygon_count = Column(Integer, nullable=False)
    n_floors_bound = Column(Integer, nullable=False, default=3)
    landcover_class = Column(String(50), nullable=True)
    access_road_class = Column(String(100), nullable=True)
    access_road_width_m = Column(Numeric(8, 2), nullable=True)
    district_code = Column(String(20), nullable=False)
    source_dataset_version = Column(String(30), nullable=False)
    
    # Relationships
    premises = relationship("Premises", backref="clusters")
    
    __table_args__ = (
        Index("idx_cluster_geom", geom, postgresql_using="gist"),
        Index("idx_cluster_district", district_code),
    )


# =============================================================================
# TABLE 4: INVOICE_LINE
# =============================================================================

class InvoiceLine(Base):
    """
    Table: invoice_line (Section 15.4)
    
    Individual invoice line items with value, quantity, HSN.
    
    Fields:
    - line_id: UUID primary key
    - supplier_gstin: FK to registration
    - recipient_gstin: Nullable for B2C invoices
    - document_date: Invoice date
    - hsn: 8-character commodity code
    - quantity: Declared quantity (nullable)
    - uqc: Unit quantity code
    - quantity_kg: Derived normalized quantity (null if normalization failed)
    - uqc_conversion_status: exact/estimated/failed
    - taxable_value: Total value of line
    - tax_amount: GST amount
    - place_of_supply: State/destination
    - supply_type: domestic/export/sez/deemed_export
    """
    __tablename__ = "invoice_line"
    
    line_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    supplier_gstin = Column(String(15), ForeignKey("registration.gstin"), nullable=False)
    recipient_gstin = Column(String(15), nullable=True)
    document_date = Column(Date, nullable=False)
    hsn = Column(String(8), nullable=False, index=True)
    quantity = Column(Numeric(20, 6), nullable=True)
    uqc = Column(String(10), nullable=True)
    quantity_kg = Column(Numeric(20, 6), nullable=True)
    uqc_conversion_status = Column(String(50), nullable=False)
    taxable_value = Column(Numeric(20, 2), nullable=False)
    tax_amount = Column(Numeric(20, 2), nullable=False)
    place_of_supply = Column(Text, nullable=False)
    supply_type = Column(String(50), nullable=False)
    
    # Relationships
    movements = relationship("MovementRecord", back_populates="invoice_line")
    
    __table_args__ = (
        Index("idx_invoice_supplier_date", supplier_gstin, document_date),
        Index("idx_invoice_hsn", hsn),
    )


# =============================================================================
# TABLE 5: MOVEMENT_RECORD
# =============================================================================

class MovementRecord(Base):
    """
    Table: movement_record (Section 15.5)
    
    E-way bill dispatch information for attribution (Rank-1 method).
    
    Fields:
    - movement_id: UUID primary key
    - line_id: FK to invoice_line
    - origin_premises_id: FK to premises (basis for movement-derived attribution)
    - origin_address_raw: As declared in e-way bill
    - destination_address_raw: Destination address
    - distance_km: Transport distance
    - vehicle_id_hash: Hashed vehicle number
    - declared_gross_weight_kg: Weight from e-way bill
    - generated_at: Timestamp
    """
    __tablename__ = "movement_record"
    
    movement_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    line_id = Column(PGUUID(as_uuid=True), ForeignKey("invoice_line.line_id"), nullable=True)
    origin_premises_id = Column(PGUUID(as_uuid=True), ForeignKey("premises.premises_id"), nullable=True)
    origin_address_raw = Column(Text, nullable=False)
    destination_address_raw = Column(Text, nullable=False)
    distance_km = Column(Numeric(10, 2), nullable=True)
    vehicle_id_hash = Column(Text, nullable=True)
    declared_gross_weight_kg = Column(Numeric(15, 2), nullable=True)
    generated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    invoice_line = relationship("InvoiceLine", back_populates="movements")
    origin_premises = relationship("Premises", back_populates="movement_records")
    
    __table_args__ = (
        Index("idx_movement_premises", origin_premises_id),
        Index("idx_movement_date", generated_at),
    )


# =============================================================================
# TABLE 6: RETURN_SUMMARY
# =============================================================================

class ReturnSummary(Base):
    """
    Table: return_summary (Section 15.6)
    
    Periodic filing summaries (GSTR-3B style).
    
    Fields:
    - gstin + period: Composite primary key
    - outward_value: Total sales
    - itc_availed: Input tax credit claimed
    - tax_paid_cash: Tax paid in money (not via credit)
    - closing_credit_balance: Remaining credit
    - filing_status: filed/late/not_filed
    """
    __tablename__ = "return_summary"
    
    gstin = Column(String(15), ForeignKey("registration.gstin"), primary_key=True)
    period = Column(String(7), primary_key=True)  # YYYY-MM format
    outward_value = Column(Numeric(20, 2), nullable=False)
    itc_availed = Column(Numeric(20, 2), nullable=False)
    tax_paid_cash = Column(Numeric(20, 2), nullable=False)
    closing_credit_balance = Column(Numeric(20, 2), nullable=False)
    filing_status = Column(String(50), nullable=False)
    
    __table_args__ = (
        CheckConstraint("outward_value >= 0", name="check_outward_positive"),
        CheckConstraint("itc_availed >= 0", name="check_itc_non_negative"),
        CheckConstraint("tax_paid_cash >= 0", name="check_cash_positive"),
    )


# =============================================================================
# TABLE 7: REFUND_CLAIM
# =============================================================================

class RefundClaim(Base):
    """
    Table: refund_claim (Section 15.7)
    
    Refund applications triggering P0 trigger.
    
    Fields:
    - claim_id: UUID primary key
    - gstin: FK to registration
    - period_from/to: Claim period
    - route: Zero-rated export / SEZ / inverted duty / other
    - amount_claimed: Total refund requested
    """
    __tablename__ = "refund_claim"
    
    claim_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    gstin = Column(String(15), ForeignKey("registration.gstin"), nullable=False, index=True)
    period_from = Column(Date, nullable=False)
    period_to = Column(Date, nullable=False)
    route = Column(String(50), nullable=False)
    amount_claimed = Column(Numeric(20, 2), nullable=False)
    
    # Relationships
    registration = relationship("Registration", back_populates="refund_claims")
    findings = relationship("Finding", back_populates="claim")
    
    __table_args__ = (
        CheckConstraint("period_to >= period_from", name="check_period_order"),
        CheckConstraint("amount_claimed > 0", name="check_amount_positive"),
    )


# =============================================================================
# TABLE 8: ATTRIBUTION
# =============================================================================

class Attribution(Base):
    """
    Table: attribution (Section 15.8)
    
    Materialised output of throughput assignment to premises.
    Every rupee attributed to exactly ONE premises (Invariant I1).
    
    Fields:
    - gstin + period + premises_id: Composite primary key
    - attributed_value: Value assigned to this premises
    - attributed_mass_kg: Mass assigned (null if UQC normalization failed)
    - method: movement_derived/even_split/principal_only
    - confidence: high/low
    """
    __tablename__ = "attribution"
    
    gstin = Column(String(15), ForeignKey("registration.gstin"), primary_key=True)
    period = Column(String(7), primary_key=True)  # YYYY-MM format
    premises_id = Column(PGUUID(as_uuid=True), ForeignKey("premises.premises_id"), primary_key=True)
    attributed_value = Column(Numeric(20, 2), nullable=False)
    attributed_mass_kg = Column(Numeric(15, 2), nullable=True)
    method = Column(String(50), nullable=False)
    confidence = Column(String(50), nullable=False)
    
    # Relationships
    premises = relationship("Premises", back_populates="attributions")
    
    __table_args__ = (
        Index("idx_attribution_period", period),
    )


# =============================================================================
# TABLE 9: FINDING
# =============================================================================

class Finding(Base):
    """
    Table: finding (Section 15.9)
    
    Detector results with scores and human-readable findings.
    Suppressed findings are persisted with blocked_reason, never deleted.
    
    Fields:
    - finding_id: UUID primary key
    - claim_id: FK to refund_claim
    - detector: Which detector produced this (D1-D4)
    - score: [0, 1] detection score
    - confidence: [0, 1] confidence level
    - finding_text: Human-readable explanation for officer
    - evidence_refs: List of pointers to source records
    - blocked_reason: Why finding was suppressed (nullable = active)
    """
    __tablename__ = "finding"
    
    finding_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    claim_id = Column(PGUUID(as_uuid=True), ForeignKey("refund_claim.claim_id"), nullable=False, index=True)
    detector = Column(String(20), nullable=False)
    score = Column(Numeric(5, 4), nullable=False)  # Range [0, 1]
    confidence = Column(Numeric(5, 4), nullable=False)  # Range [0, 1]
    finding_text = Column(Text, nullable=False)
    evidence_refs = Column(ARRAY(String), nullable=False)
    blocked_reason = Column(String(50), nullable=True)
    
    # Relationships
    claim = relationship("RefundClaim", back_populates="findings")
    
    __table_args__ = (
        Index("idx_finding_detector", detector),
        Index("idx_finding_blocked", blocked_reason),
    )
