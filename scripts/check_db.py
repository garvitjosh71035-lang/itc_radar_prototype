#!/usr/bin/env python3
"""Check and seed production database with sample data"""

import os
from sqlalchemy import create_engine, text

db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("❌ DATABASE_URL not set!")
    exit(1)

engine = create_engine(db_url)

with engine.connect() as conn:
    # Check if tables exist
    result = conn.execute(text("SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'registration');"))
    table_exists = result.scalar()[0]
    
    if not table_exists:
        print("⚠️  Tables don't exist yet!")
        print("Creating tables...")
        
        # Create tables
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS registration (
                gstin VARCHAR(15) PRIMARY KEY,
                legal_name TEXT,
                pan VARCHAR(10),
                constitution VARCHAR(50),
                registration_date DATE,
                status VARCHAR(50) DEFAULT 'active',
                declared_role VARCHAR(50),
                declared_hsn VARCHAR(8)[],
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS invoice_line (
                line_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                supplier_gstin VARCHAR(15),
                recipient_gstin VARCHAR(15),
                document_date DATE,
                hsn VARCHAR(8),
                quantity_kg NUMERIC(20,6),
                uqc VARCHAR(10),
                uqc_conversion_status VARCHAR(50),
                taxable_value NUMERIC(20,2),
                tax_amount NUMERIC(20,2),
                place_of_supply TEXT,
                supply_type VARCHAR(50)
            )
        """))
        
        print("✅ Tables created!")
    
    # Count registrations
    result = conn.execute(text("SELECT COUNT(*) FROM registration;"))
    count = result.scalar()
    print(f"📊 Registrations in database: {count}")
    
    if count == 0:
        print("\n📝 Adding sample data...")
        
        # Add sample fraud case
        conn.execute(text("""
            INSERT INTO registration (gstin, legal_name, pan, constitution, registration_date, declared_role, declared_hsn) VALUES 
            ('P2OVER0001', 'Export House One', 'ABCDE1234F', 'private_ltd', '2025-06-01', 'manufacturer', ARRAY['540792'])
            ON CONFLICT (gstin) DO NOTHING
        """))
        
        # Add sample clean case
        conn.execute(text("""
            INSERT INTO registration (gstin, legal_name, pan, constitution, registration_date, declared_role, declared_hsn) VALUES 
            ('CLEAN0042', 'Genuine Traders Ltd', 'FGHIJ5678K', 'private_ltd', '2023-01-15', 'trader', ARRAY['520831'])
            ON CONFLICT (gstin) DO NOTHING
        """))
        
        # Add invoices
        conn.execute(text("""
            INSERT INTO invoice_line (line_id, supplier_gstin, document_date, hsn, quantity_kg, taxable_value, supply_type, uqc, uqc_conversion_status) VALUES 
            (gen_random_uuid(), 'P2OVER0001', '2026-08-01', '540792', 760.0, 2394000.0, 'export', 'KGM', 'exact'),
            (gen_random_uuid(), 'CLEAN0042', '2026-08-01', '520831', 1000.0, 280000.0, 'domestic', 'KGM', 'exact')
            ON CONFLICT DO NOTHING
        """))
        
        print("✅ Sample data added!")
    
    # Show what's in database
    result = conn.execute(text("SELECT gstin, legal_name, declared_role FROM registration ORDER BY gstin;"))
    print("\n📋 Database contents:")
    for row in result:
        print(f"   • {row[0]} - {row[1]} ({row[2]})")
    
    print("\n✅ Database ready!")
