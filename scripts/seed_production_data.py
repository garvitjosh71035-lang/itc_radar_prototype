#!/usr/bin/env python3
"""
Quick seed script for production database
Run this after adding DATABASE_URL to local environment
"""

import os
import sys
from sqlalchemy import create_engine, text
from uuid import uuid4

# Set database URL from environment
db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("❌ Error: DATABASE_URL environment variable not set!")
    print("Set it using: export DATABASE_URL='<your-postgres-url>'")
    sys.exit(1)

print(f"🔗 Connecting to database: {db_url[:50]}...")

engine = create_engine(db_url)

with engine.connect() as conn:
    # Create tables
    print("📝 Creating tables...")
    
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS registration (
            gstin VARCHAR(15) PRIMARY KEY,
            legal_name TEXT,
            pan VARCHAR(10),
            constitution VARCHAR(50),
            registration_date DATE,
            status VARCHAR(50) DEFAULT 'active',
            declared_role VARCHAR(50),
            declared_hsn VARCHAR(8)[]
        )
    """))
    
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS invoice_line (
            line_id UUID PRIMARY KEY,
            supplier_gstin VARCHAR(15),
            recipient_gstin VARCHAR(15),
            document_date DATE,
            hsn VARCHAR(8),
            quantity_kg NUMERIC(20,6),
            uqc VARCHAR(10),
            quantity_kg_calc NUMERIC(20,6),
            uqc_conversion_status VARCHAR(50),
            taxable_value NUMERIC(20,2),
            tax_amount NUMERIC(20,2),
            place_of_supply TEXT,
            supply_type VARCHAR(50)
        )
    """))
    
    print("✅ Tables created!")
    
    # Insert sample registrations
    print("📊 Inserting sample data...")
    
    conn.execute(text("""
        INSERT INTO registration (gstin, legal_name, pan, constitution, registration_date, declared_role, declared_hsn) VALUES 
        ('P2OVER0001', 'Export House One', 'ABCDE1234F', 'private_ltd', '2025-06-01', 'manufacturer', ARRAY['540792']),
        ('CLEAN0042', 'Genuine Traders Ltd', 'FGHIJ5678K', 'private_ltd', '2023-01-15', 'trader', ARRAY['520831'])
        ON CONFLICT (gstin) DO NOTHING
    """))
    
    conn.execute(text("""
        INSERT INTO invoice_line (line_id, supplier_gstin, document_date, hsn, quantity_kg, taxable_value, supply_type, uqc, uqc_conversion_status) VALUES 
        (gen_random_uuid(), 'P2OVER0001', '2026-08-01', '540792', 760.0, 2394000.0, 'export', 'KGM', 'exact'),
        (gen_random_uuid(), 'CLEAN0042', '2026-08-01', '520831', 1000.0, 280000.0, 'domestic', 'KGM', 'exact')
        ON CONFLICT DO NOTHING
    """))
    
    print("✅ Sample data inserted!")
    print("\n🎉 Database seeded successfully!")
    print("\nTo query:")
    print("SELECT * FROM registration;")
    print("SELECT * FROM invoice_line;")
