-- PACE Database Initialization Script
-- Creates tables and indexes for PostgreSQL with PostGIS extension

-- Enable PostGIS extension (must be done in a separate transaction)
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS h3;  -- For spatial indexing (optional)

-- Create ENUM types first (referenced by tables)
DO $$ BEGIN
    CREATE TYPE constitution_type AS ENUM ('proprietorship', 'partnership', 'llp', 'private_ltd', 'public_ltd', 'huf', 'trust', 'other');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE registration_status AS ENUM ('active', 'suspended', 'cancelled', 'provisional');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE declared_role AS ENUM ('manufacturer', 'trader', 'warehouse', 'job_worker', 'service', 'mixed');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE premises_type AS ENUM ('principal', 'additional');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE geocode_tier AS ENUM ('rooftop', 'building_centroid', 'street', 'locality_centroid', 'unresolved');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE join_status AS ENUM ('matched', 'candidate', 'ambiguous', 'unresolved', 'no_structure');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE supply_type AS ENUM ('domestic', 'export', 'sez_supply', 'deemed_export');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE refund_route AS ENUM ('zero_rated_export', 'sez_supply', 'inverted_duty', 'other');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE attribution_method AS ENUM ('movement_derived', 'even_split', 'principal_only');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE attribution_confidence AS ENUM ('high', 'low');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE detector_name AS ENUM ('D1', 'D2a', 'D2b', 'D3', 'D4');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE blocked_reason AS ENUM ('low_geocode_confidence', 'role_gate', 'unsourced_parameter', 'low_attribution_confidence', 'ambiguous_join');
EXCEPTION WHEN duplicate_object THEN null; END $$;


-- =============================================================================
-- TABLE: registration (Section 15.1)
-- =============================================================================
CREATE TABLE IF NOT EXISTS registration (
    gstin VARCHAR(15) PRIMARY KEY CHECK (LENGTH(gstin) = 15),
    legal_name TEXT NOT NULL,
    pan VARCHAR(10) NOT NULL,
    constitution constitution_type NOT NULL,
    registration_date DATE NOT NULL,
    status registration_status NOT NULL DEFAULT 'active',
    cancellation_date DATE,
    declared_role declared_role,
    declared_hsn VARCHAR(8)[] NOT NULL,
    authorised_signatory_id TEXT,
    bank_account_hash TEXT[],
    contact_hash TEXT[],
    
    CONSTRAINT valid_gstin_checksum CHECK (gstin ~ '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]$')
);

CREATE INDEX idx_registration_pan ON registration(pan);
CREATE INDEX idx_registration_status ON registration(status);


-- =============================================================================
-- TABLE: premises (Section 15.2)
-- =============================================================================
CREATE TABLE IF NOT EXISTS premises (
    premises_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gstin VARCHAR(15) NOT NULL REFERENCES registration(gstin),
    premises_type premises_type NOT NULL,
    address_raw TEXT NOT NULL,
    geom GEOGRAPHY(POINT, 4326),
    geocode_tier geocode_tier NOT NULL,
    geocode_source TEXT NOT NULL,
    cluster_id UUID,
    join_status join_status NOT NULL,
    goods_capable BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_premises_gstin ON premises(gstin);
CREATE INDEX idx_premises_geom ON premises USING GIST (geom);
CREATE INDEX idx_premises_cluster ON premises(cluster_id);


-- =============================================================================
-- TABLE: premises_cluster (Section 15.3)
-- =============================================================================
CREATE TABLE IF NOT EXISTS premises_cluster (
    cluster_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    geom GEOMETRY(MULTIPOLYGON, 4326) NOT NULL UNIQUE,
    area_m2 NUMERIC(12, 2) NOT NULL,
    polygon_count INTEGER NOT NULL,
    n_floors_bound INTEGER NOT NULL DEFAULT 3,
    landcover_class VARCHAR(50),
    access_road_class VARCHAR(100),
    access_road_width_m NUMERIC(8, 2),
    district_code VARCHAR(20) NOT NULL,
    source_dataset_version VARCHAR(30) NOT NULL
);

CREATE UNIQUE INDEX idx_cluster_geom ON premises_cluster USING GIST (geom);
CREATE INDEX idx_cluster_district ON premises_cluster(district_code);


-- =============================================================================
-- TABLE: invoice_line (Section 15.4)
-- =============================================================================
CREATE TABLE IF NOT EXISTS invoice_line (
    line_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_gstin VARCHAR(15) NOT NULL REFERENCES registration(gstin),
    recipient_gstin VARCHAR(15),
    document_date DATE NOT NULL,
    hsn VARCHAR(8) NOT NULL,
    quantity NUMERIC(20, 6),
    uqc VARCHAR(10),
    quantity_kg NUMERIC(20, 6),
    uqc_conversion_status VARCHAR(20) NOT NULL CHECK (uqc_conversion_status IN ('exact', 'estimated', 'failed')),
    taxable_value NUMERIC(20, 2) NOT NULL,
    tax_amount NUMERIC(20, 2) NOT NULL,
    place_of_supply TEXT NOT NULL,
    supply_type supply_type NOT NULL
);

CREATE INDEX idx_invoice_supplier_date ON invoice_line(supplier_gstin, document_date);
CREATE INDEX idx_invoice_hsn ON invoice_line(hsn);


-- =============================================================================
-- TABLE: movement_record (Section 15.5)
-- =============================================================================
CREATE TABLE IF NOT EXISTS movement_record (
    movement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    line_id UUID REFERENCES invoice_line(line_id),
    origin_premises_id UUID REFERENCES premises(premises_id),
    origin_address_raw TEXT NOT NULL,
    destination_address_raw TEXT NOT NULL,
    distance_km NUMERIC(10, 2),
    vehicle_id_hash TEXT,
    declared_gross_weight_kg NUMERIC(15, 2),
    generated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_movement_premises ON movement_record(origin_premises_id);
CREATE INDEX idx_movement_date ON movement_record(generated_at);


-- =============================================================================
-- TABLE: return_summary (Section 15.6)
-- =============================================================================
CREATE TABLE IF NOT EXISTS return_summary (
    gstin VARCHAR(15) NOT NULL REFERENCES registration(gstin),
    period VARCHAR(7) NOT NULL,  -- YYYY-MM format
    outward_value NUMERIC(20, 2) NOT NULL,
    itc_availed NUMERIC(20, 2) NOT NULL,
    tax_paid_cash NUMERIC(20, 2) NOT NULL,
    closing_credit_balance NUMERIC(20, 2) NOT NULL,
    filing_status VARCHAR(20) NOT NULL CHECK (filing_status IN ('filed', 'late', 'not_filed')),
    
    PRIMARY KEY (gstin, period),
    
    CONSTRAINT check_outward_positive CHECK (outward_value >= 0),
    CONSTRAINT check_itc_non_negative CHECK (itc_availed >= 0),
    CONSTRAINT check_cash_positive CHECK (tax_paid_cash >= 0)
);

CREATE INDEX idx_return_period ON return_summary(period);


-- =============================================================================
-- TABLE: refund_claim (Section 15.7)
-- =============================================================================
CREATE TABLE IF NOT EXISTS refund_claim (
    claim_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gstin VARCHAR(15) NOT NULL REFERENCES registration(gstin),
    period_from DATE NOT NULL,
    period_to DATE NOT NULL,
    route refund_route NOT NULL,
    amount_claimed NUMERIC(20, 2) NOT NULL,
    
    CONSTRAINT check_period_order CHECK (period_to >= period_from),
    CONSTRAINT check_amount_positive CHECK (amount_claimed > 0)
);

CREATE INDEX idx_refund_gstin ON refund_claim(gstin);
CREATE INDEX idx_refund_period ON refund_claim(period_from, period_to);


-- =============================================================================
-- TABLE: attribution (Section 15.8)
-- =============================================================================
CREATE TABLE IF NOT EXISTS attribution (
    gstin VARCHAR(15) NOT NULL REFERENCES registration(gstin),
    period VARCHAR(7) NOT NULL,
    premises_id UUID NOT NULL REFERENCES premises(premises_id),
    attributed_value NUMERIC(20, 2) NOT NULL,
    attributed_mass_kg NUMERIC(15, 2),
    method attribution_method NOT NULL,
    confidence attribution_confidence NOT NULL,
    
    PRIMARY KEY (gstin, period, premises_id)
);

CREATE INDEX idx_attribution_period ON attribution(period);


-- =============================================================================
-- TABLE: finding (Section 15.9)
-- =============================================================================
CREATE TABLE IF NOT EXISTS finding (
    finding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID NOT NULL REFERENCES refund_claim(claim_id),
    detector detector_name NOT NULL,
    score NUMERIC(5, 4) NOT NULL CHECK (score >= 0 AND score <= 1),
    confidence NUMERIC(5, 4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    finding_text TEXT NOT NULL,
    evidence_refs TEXT[] NOT NULL,
    blocked_reason blocked_reason,
    
    CHECK ((blocked_reason IS NULL AND score > 0) OR blocked_reason IS NOT NULL)
);

CREATE INDEX idx_finding_detector ON finding(detector);
CREATE INDEX idx_finding_blocked ON finding(blocked_reason);
CREATE INDEX idx_finding_claim ON finding(claim_id);


-- =============================================================================
-- TRIGGERS (if needed for audit trails)
-- =============================================================================

-- Add audit timestamps
ALTER TABLE registration ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
ALTER TABLE registration ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();

-- Function to update timestamp on row modification
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to registration table
DROP TRIGGER IF EXISTS update_registration_timestamp ON registration;
CREATE TRIGGER update_registration_timestamp 
    BEFORE UPDATE ON registration 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();


-- =============================================================================
-- SEED DATA (For testing - comment out in production)
-- =============================================================================

-- Insert sample registration
INSERT INTO registration (gstin, legal_name, pan, constitution, registration_date, status, declared_role, declared_hsn) VALUES
('27ABCDE1234F1Z5', 'SAMPLE EXPORT PRIVATE LIMITED', 'ABCDE1234F', 'private_ltd', '2025-01-15', 'active', 'manufacturer', ARRAY['540792'])
ON CONFLICT (gstin) DO NOTHING;


-- =============================================================================
-- VIEWS (Optional useful views)
-- =============================================================================

-- View: Entity summary with total outward value
CREATE VIEW IF NOT EXISTS entity_summary AS
SELECT 
    r.gstin,
    r.legal_name,
    r.declared_role,
    COUNT(DISTINCT rl.line_id) as invoice_count,
    COALESCE(SUM(rl.taxable_value), 0) as total_outward_value,
    MAX(rl.document_date) as last_invoice_date
FROM registration r
LEFT JOIN invoice_line rl ON r.gstin = rl.supplier_gstin
GROUP BY r.gstin, r.legal_name, r.declared_role;


-- View: Premises utilization
CREATE VIEW IF NOT EXISTS premises_utilization AS
SELECT 
    pc.cluster_id,
    pc.area_m2,
    COUNT(DISTINCT p.premises_id) as entity_count,
    ROUND(CAST(pc.area_m2 / NULLIF(COUNT(DISTINCT p.premises_id), 0) AS NUMERIC), 2) as area_per_entity
FROM premises_cluster pc
LEFT JOIN premises p ON p.cluster_id = pc.cluster_id
GROUP BY pc.cluster_id, pc.area_m2;

COMMENT ON VIEW premises_utilization IS 'Shows entity density per square metre of building footprint';


-- =============================================================================
-- COMMENTS ON COLUMNS (Documentation)
-- =============================================================================

COMMENT ON TABLE registration IS 'Section 15.1: GST registration details, PAN, constitutional type, HSN codes involved';
COMMENT ON TABLE premises IS 'Section 15.2: Registered business premises with geocoded locations and spatial joins';
COMMENT ON TABLE premises_cluster IS 'Section 15.3: Dissolved building polygons within 5m buffer, unit of analysis for D2a/D3';
COMMENT ON TABLE invoice_line IS 'Section 15.4: Invoice line items with normalized quantities and values';
COMMENT ON TABLE movement_record IS 'Section 15.5: E-way bill dispatch information for attribution';
COMMENT ON TABLE return_summary IS 'Section 15.6: Periodic tax filing summaries (GSTR-3B style)';
COMMENT ON TABLE refund_claim IS 'Section 15.7: Refund applications triggering risk assessment';
COMMENT ON TABLE attribution IS 'Section 15.8: Throughput assignment to specific premises, respects invariant I1';
COMMENT ON TABLE finding IS 'Section 15.9: Detector outputs with scores, human-readable findings, and suppression reasons';


-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_invoice_key_columns ON invoice_line(supplier_gstin, hsn, document_date);

-- Spatial index for premises queries  
CREATE INDEX IF NOT EXISTS idx_premises_geo ON premises USING GIST (geom);

-- Partial index for active registrations only
CREATE INDEX IF NOT EXISTS idx_registration_active ON registration(pan) WHERE status = 'active';
