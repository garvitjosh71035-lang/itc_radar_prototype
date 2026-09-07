#!/usr/bin/env python3
"""
Database seeding script for PACE prototype.

Loads synthetic data from JSON files into PostgreSQL/PostGIS database.
Used after generating synthetic data.

Usage:
    python seed_db.py --overwrite
"""

import json
import sys
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.database import engine, Base, LocalSession
from app.models import Registration, InvoiceLine, ReturnSummary, RefundClaim

def load_json_file(filename: str) -> list:
    """Load JSON file."""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found. Run generate_synthetic_data.py first.")
        sys.exit(1)


def seed_database(entities: list, invoices: list, refund_claims: list, db: Session):
    """Seed database with synthetic data."""
    
    print("Seeding database...")
    
    # Check if already seeded
    existing = db.query(Registration).count()
    if existing > 0:
        print(f"Warning: Database already contains {existing} entities.")
        print("Use --overwrite flag to clear and re-seed.")
        return
    
    # Clear existing data
    db.query(RefundClaim).delete()
    db.query(ReturnSummary).delete()
    db.query(InvoiceLine).delete()
    db.query(Registration).delete()
    
    db.commit()
    print("Cleared existing data.")
    
    # Insert registrations
    print(f"\nInserting {len(entities)} registrations...")
    registrations = []
    
    for entity in entities:
        reg = Registration(
            gstin=entity["gstin"],
            legal_name=entity["legal_name"],
            pan=entity["pan"],
            constitution=getattr(entity["constitution"], entity[entity["constitution"]], "private_ltd"),
            registration_date=date.fromisoformat(entity.get("registration_date", "2025-01-01")),
            declared_role=entity.get("declared_role"),
            declared_hsn=entity.get("declared_hsn", ["540792"]),
        )
        registrations.append(reg)
        db.add(reg)
    
    db.flush()
    print(f"  ✓ Inserted {len(registrations)} registrations")
    
    # Insert invoice lines
    print(f"\nInserting {len(invoices)} invoice lines...")
    for inv in invoices:
        invoice = InvoiceLine(
            supplier_gstin=inv["supplier_gstin"],
            recipient_gstin=inv.get("recipient_gstin"),
            document_date=date.fromisoformat(inv["document_date"]) if isinstance(inv["document_date"], str) else inv["document_date"],
            hsn=inv["hsn"],
            quantity_kg=inv.get("quantity_kg"),
            taxable_value=inv["taxable_value"],
            tax_amount=inv.get("tax_amount", 0),
            place_of_supply=inv.get("place_of_supply", "Gujarat"),
            supply_type=inv.get("supply_type", "domestic"),
            uqc="KGM" if inv.get("quantity_kg") else None,
            uqc_conversion_status="exact",
        )
        db.add(invoice)
    
    db.flush()
    print(f"  ✓ Inserted {len(invoices)} invoice lines")
    
    # Insert refund claims
    print(f"\nInserting {len(refund_claims)} refund claims...")
    for claim in refund_claims:
        refund_claim = RefundClaim(
            gstin=claim["gstin"],
            period_from=date.today() - timedelta(days=90),
            period_to=date.today(),
            route="zero_rated_export",
            amount_claimed=claim["amount_claimed"],
        )
        db.add(refund_claim)
    
    db.commit()
    print(f"  ✓ Inserted {len(refund_claims)} refund claims")
    
    print("\n✓ Database seeded successfully!")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed PACE database with synthetic data")
    parser.add_argument("--entities-file", default="./data/entities.json", help="Entities JSON file")
    parser.add_argument("--invoices-file", default="./data/invoices.json", help="Invoices JSON file")
    parser.add_argument("--refunds-file", default="./data/refund_claims.json", help="Refund claims JSON file")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing data")
    
    args = parser.parse_args()
    
    # Load JSON files
    entities = load_json_file(args.entities_file)
    invoices = load_json_file(args.invoices_file)
    refund_claims = load_json_file(args.refunds_file)
    
    # Create session
    db = LocalSession()
    
    try:
        seed_database(entities, invoices, refund_claims, db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
