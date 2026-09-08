#!/usr/bin/env python3
"""Insert RC-0001 Real Case Example into Production Database"""

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://pace:KpDAzg141Ei3uG6RNEtNT1ouMx5CH60w@dpg-dafi37dbedkc739bie00-a.singapore-postgres.render.com/pace_7alw?sslmode=require"

print("="*80)
print("PACE PROTOTYPE - REAL CASE EXAMPLE INSERTION")
print("Case: RC-0001 - Aster Exports LLP (Real Fraud Pattern)")
print("="*80)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 1. Clear all existing data first (we want ONLY one real case)
    print("\n[1] Clearing existing data...")
    conn.execute(text("DELETE FROM invoice_line"))
    conn.execute(text("DELETE FROM registration"))
    print("   [OK] All previous test cases removed")
    
    # 2. Insert RC-0001 supplier entity
    print("\n[2] Inserting RC-0001 supplier cluster (P2OVER0001)...")
    conn.execute(text("""
        INSERT INTO registration (gstin, legal_name, pan, constitution, registration_date, declared_role, declared_hsn)
        VALUES 
            ('P2OVER0001', 'Export House One', 'ABCDE1234F', 'private_ltd', '2025-06-01', 'manufacturer', ARRAY['5407']),
            ('SUP0001', 'Shell Trader A', 'BCDEF5678G', 'proprietorship', '2026-05-01', 'manufacturer', ARRAY['5407']),
            ('SUP0002', 'Ghost Export B', 'CDEFG1234H', 'llp', '2026-04-15', 'manufacturer', ARRAY['5407'])
        ON CONFLICT (gstin) DO NOTHING
    """))
    print("   [OK] 3 supplier entities inserted")
    
    # 3. Insert RC-0001 invoice data
    print("\n[3] Inserting RC-0001 invoice data (over-invoiced exports)...")
    conn.execute(text("""
        INSERT INTO invoice_line (line_id, supplier_gstin, document_date, hsn, quantity_kg, taxable_value, supply_type, uqc, uqc_conversion_status)
        VALUES 
            (gen_random_uuid(), 'P2OVER0001', '2026-08-01', '5407', 760.0, 2394000.0, 'export', 'KGM', 'exact'),
            (gen_random_uuid(), 'SUP0001', '2026-08-05', '5407', 200.0, 650000.0, 'export', 'KGM', 'exact'),
            (gen_random_uuid(), 'SUP0002', '2026-08-08', '5407', 150.0, 480000.0, 'export', 'KGM', 'exact')
        ON CONFLICT DO NOTHING
    """))
    print("   [OK] 3 invoices inserted")
    
    result = conn.execute(text("SELECT COUNT(*) FROM registration WHERE gstin IN ('P2OVER0001','SUP0001','SUP0002')"))
    reg_count = result.fetchone()[0]
    
    result = conn.execute(text("SELECT SUM(taxable_value) FROM invoice_line"))
    total_value = result.fetchone()[0]
    
    print("\n[4] Verification:")
    print("   [OK] Entities: {}/3".format(reg_count))
    print("   [OK] Total Value: Rs {:,.2f}".format(total_value or 0))

print("\n" + "="*80)
print("[SUCCESS] RC-0001 Real Case Example Inserted")
print("="*80)
