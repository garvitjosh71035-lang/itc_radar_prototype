#!/usr/bin/env python3
"""
Synthetic GST Data Generator for PACE Prototype

Generates realistic synthetic GST data following workflow.md Section 11 (Synthetic Dataset Specification).

Creates:
- P1-P5 fraud patterns (positives)
- N1-N6 hard negatives (legitimate cases)
- Realistic invoice networks and refund claims

Usage:
    python generate_synthetic_data.py --entities 200 --district surat
"""

import argparse
import random
from datetime import date, timedelta
from typing import List, Dict, Any
from uuid import uuid4
import json

# Configuration
DEFAULT_ENTITIES = 200
FRAUD_PREVALENCE = 0.02  # 2% as per workflow.md Section 16.4
MIN_HSN_SAMPLES = 200


class SyntheticDataGenerator:
    """Generate synthetic GST data with injected fraud patterns."""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.entities = []
        self.invoices = []
        self.refund_claims = []
        
        # Mock HSN codes used in fraud cases
        self.hsn_codes = [
            "540792",  # Woven synthetic fabrics (work example HSN)
            "520831",  # Cotton woven fabric
            "610910",  # T-shirts cotton
            "620343",  # Men's trousers
            "851713",  # Mobile phones
            "090420",  # Black pepper
            "071320",  # Pulses
            "100630",  # Rice
            "500790",  # Silk fabrics
            "640351",  # Footwear
        ]
        
        # Unit price benchmarks (₹/kg) - from DGCI&S mock data
        self.hsn_benchmarks = {
            "540792": {"median": 150.0, "mad_scale": 0.42},
            "520831": {"median": 280.0, "mad_scale": 0.38},
            "610910": {"median": 180.0, "mad_scale": 0.35},
            "620343": {"median": 1200.0, "mad_scale": 0.45},
            "851713": {"median": 850.0, "mad_scale": 0.40},
            "090420": {"median": 450.0, "mad_scale": 0.50},
            "071320": {"median": 90.0, "mad_scale": 0.45},
            "100630": {"median": 75.0, "mad_scale": 0.40},
            "500790": {"median": 900.0, "mad_scale": 0.55},
            "640351": {"median": 320.0, "mad_scale": 0.42},
        }
        
        # Mock districts in India
        self.districts = [
            {"name": "Surat", "state": "Gujarat", "code": "GUJ_SUR"},
            {"name": "Ahmedabad", "state": "Gujarat", "code": "GUJ_AHM"},
            {"name": "Mumbai", "state": "Maharashtra", "code": "MAH_MUM"},
            {"name": "Delhi", "state": "Delhi", "code": "DEL_NCR"},
            {"name": "Coimbatore", "state": "Tamil Nadu", "code": "TN_CBE"},
            {"name": "Rural Tamil Nadu", "state": "Tamil Nadu", "code": "TN_RUR"},
        ]
    
    def generate_entities(self, count: int, district: str = "Surat"):
        """
        Generate synthetic GST entities with fraud and hard negative patterns.
        
        Creates:
        - P1-P5 fraud patterns (2% prevalence)
        - N1-N6 hard negatives (5% total)
        - Clean legitimate entities (93%)
        """
        num_frauds = int(count * FRAUD_PREVALENCE)
        num_hard_negatives = int(count * 0.05)
        num_clean = count - num_frauds - num_hard_negatives
        
        print(f"Generating {count} entities:")
        print(f"  - Fraud patterns: {num_frauds}")
        print(f"  - Hard negatives: {num_hard_negatives}")
        print(f"  - Clean entities: {num_clean}")
        
        self.entities = []
        
        # Generate fraud patterns
        self.entities.extend(self._generate_p1_shell_chain(int(num_frauds * 0.2)))
        self.entities.extend(self._generate_p2_over_invoicing(int(num_frauds * 0.2)))
        self.entities.extend(self._generate_p3_circular_trading(int(num_frauds * 0.15)))
        self.entities.extend(self._generate_p4_volume_inflation(int(num_frauds * 0.15)))
        self.entities.extend(self._generate_p5_footprint_collision(int(num_frauds * 0.3)))
        
        # Generate hard negatives
        self.entities.extend(self._generate_n1_trading_company(50))
        self.entities.extend(self._generate_n2_rural_manufacturer(50))
        self.entities.extend(self._generate_n3_job_worker(20))
        self.entities.extend(self._generate_n4_premium_exporter(20))
        self.entities.extend(self._generate_n5_industrial_estate(50))
        self.entities.extend(self._generate_n6_unresolvable_address(10))
        
        # Generate clean entities
        self.entities.extend(self._generate_clean_entities(num_clean, district))
        
        random.shuffle(self.entities)
        
        return self.entities
    
    def _generate_p1_shell_chain(self, count: int) -> List[Dict[str, Any]]:
        """P1 - Pure shell chain: new entities, no cash tax, colliding at small footprint."""
        entities = []
        base_date = date.today() - timedelta(days=60)
        
        for i in range(count):
            entities.append({
                "type": "p1_shell_chain",
                "gstin": f"P1SHELL{i:04d}",
                "legal_name": f"Shell Trader {i+1}",
                "pan": f"ABCDE{i}F1Z5",
                "constitution": "proprietorship",
                "registration_date": base_date + timedelta(days=i*2),
                "declared_role": "manufacturer",
                "declared_hsn": ["540792"],
                "fraud_pattern": "pure_shell_chain",
                "characteristics": {
                    "very_new": True,  # <90 days old
                    "zero_cash_tax": True,
                    "shared_addresses": True,
                    "small_footprint": True,
                }
            })
        
        return entities
    
    def _generate_p2_over_invoicing(self, count: int) -> List[Dict[str, Any]]:
        """P2 - Over-invoiced zero-rated export: real cheap goods at absurd price."""
        entities = []
        
        for i in range(count):
            hsn = "540792"
            benchmark = self.hsn_benchmarks[hsn]
            
            entities.append({
                "type": "p2_over_invoicing",
                "gstin": f"P2OVER{i:04d}",
                "legal_name": f"Export House {i+1}",
                "pan": f"FGHIJ{i}K2Z5",
                "constitution": "private_ltd",
                "registration_date": date.today() - timedelta(days=180),
                "declared_role": "manufacturer",
                "declared_hsn": [hsn],
                "fraud_pattern": "over_invoiced_zero_rated",
                "characteristics": {
                    "unit_price_multiple": random.uniform(15, 30),  # 15-30× market price
                    "export_route": "zero_rated",
                    "real_quantity_low_value": True,
                },
                "mock_unit_price": benchmark["median"] * random.uniform(15, 30),
                "benchmark_median": benchmark["median"],
            })
        
        return entities
    
    def _generate_p3_circular_trading(self, count: int) -> List[Dict[str, Any]]:
        """P3 - Circular trading: closed loop inflating turnover."""
        entities = []
        
        for i in range(count):
            entities.append({
                "type": "p3_circular_trading",
                "gstin": f"P3CIRC{i:04d}",
                "legal_name": f"Circular Trader {i+1}",
                "pan": f"KLMNO{i}P3Z5",
                "constitution": "partnership",
                "registration_date": date.today() - timedelta(days=120),
                "declared_role": "trader",
                "declared_hsn": ["610910"],
                "fraud_pattern": "circular_trading",
                "characteristics": {
                    "closed_cycle": True,
                    "high_turnover_velocity": True,
                    "no_cash_tax_origin": True,
                }
            })
        
        return entities
    
    def _generate_p4_volume_inflation(self, count: int) -> List[Dict[str, Any]]:
        """P4 - Volume inflation: bulk commodity mass beyond premises capability."""
        entities = []
        
        for i in range(count):
            entities.append({
                "type": "p4_volume_inflation",
                "gstin": f"P4VOL{i:04d}",
                "legal_name": f"Bulk Traders {i+1}",
                "pan": f"QRSTU{i}V4Z5",
                "constitution": "llp",
                "registration_date": date.today() - timedelta(days=200),
                "declared_role": "warehouse",
                "declared_hsn": ["071320"],  # Pulses (bulk commodity)
                "fraud_pattern": "volume_inflation",
                "characteristics": {
                    "declared_mass_excessive": True,
                    "bulk_commodity": True,
                    "capacity_violation": True,
                }
            })
        
        return entities
    
    def _generate_p5_footprint_collision(self, count: int) -> List[Dict[str, Any]]:
        """P5 - Many manufacturers on tiny footprint."""
        entities = []
        
        for i in range(count):
            entities.append({
                "type": "p5_footprint_collision",
                "gstin": f"P5COLL{i:04d}",
                "legal_name": f"Micro Manufacturer {i+1}",
                "pan": f"WXYZA{i}B5Z5",
                "constitution": "proprietorship",
                "registration_date": date.today() - timedelta(days=90),
                "declared_role": "manufacturer",
                "declared_hsn": ["520831"],
                "fraud_pattern": "footprint_collision_cluster",
                "characteristics": {
                    "entity_density_high": True,
                    "tiny_footprint": True,
                    "shared_infrastructure": True,
                }
            })
        
        return entities
    
    def _generate_n1_trading_company(self, count: int) -> List[Dict[str, Any]]:
        """N1 - Legitimate trading company (no factory needed)."""
        entities = []
        
        for i in range(count):
            entities.append({
                "type": "n1_trading_company",
                "gstin": f"N1TRAD{i:04d}",
                "legal_name": f"Genuine Trader {i+1}",
                "pan": f"CDEFG{i}H1Z5",
                "constitution": "private_ltd",
                "registration_date": date.today() - timedelta(days=500),
                "declared_role": "trader",  # Key: explicitly trader, not manufacturer
                "declared_hsn": ["610910", "620343"],
                "hard_negative": "n1_trading_no_factory",
                "characteristics": {
                    "established_9_years": True,
                    "no_warehousing_needed": True,
                    "cash_to_itc_ratio": 0.28,
                }
            })
        
        return entities
    
    def _generate_n2_rural_manufacturer(self, count: int) -> List[Dict[str, Any]]:
        """N2 - Small rural manufacturer, low values."""
        entities = []
        
        for i in range(count):
            entities.append({
                "type": "n2_rural_manufacturer",
                "gstin": f"N2RUR{i:04d}",
                "legal_name": f"Rural Workshop {i+1}",
                "pan": f"IJKLM{i}N2Z5",
                "constitution": "proprietorship",
                "registration_date": date.today() - timedelta(days=400),
                "declared_role": "manufacturer",
                "declared_hsn": ["500790"],
                "hard_negative": "n2_small_rural_low_values",
                "characteristics": {
                    "rural_district": True,
                    "low_absolute_values": True,
                    "small_footprint_180m2": True,
                    "district_stratified_clears": True,
                }
            })
        
        return entities
    
    def _generate_n3_job_worker(self, count: int) -> List[Dict[str, Any]]:
        """N3 - Job-worker processing at third party's premises."""
        entities = []
        
        for i in range(count):
            entities.append({
                "type": "n3_job_worker",
                "gstin": f"N3JOB{i:04d}",
                "legal_name": f"Job Worker {i+1}",
                "pan": f"OPQRS{i}T3Z5",
                "constitution": "proprietorship",
                "registration_date": date.today() - timedelta(days=300),
                "declared_role": "job_worker",  # Key: job-worker role
                "declared_hsn": ["610910"],
                "hard_negative": "n3_job_worker_third_party_premises",
                "characteristics": {
                    "goods_processed_elsewhere": True,
                    "role_gate_exempt": True,
                }
            })
        
        return entities
    
    def _generate_n4_premium_exporter(self, count: int) -> List[Dict[str, Any]]:
        """N4 - Genuine premium exporter (legitimate high unit price)."""
        entities = []
        
        for i in range(count):
            hsn = "500790"
            benchmark = self.hsn_benchmarks[hsn]
            multiple = random.uniform(8, 12)  # Premium product
            
            entities.append({
                "type": "n4_premium_exporter",
                "gstin": f"N4PRMI{i:04d}",
                "legal_name": f"Premium Exports {i+1}",
                "pan": f"UVWXY{i}Z4Z5",
                "constitution": "private_ltd",
                "registration_date": date.today() - timedelta(days=4000),  # 11 years old
                "declared_role": "manufacturer",
                "declared_hsn": [hsn],
                "hard_negative": "n4_genuine_premium_high_price",
                "characteristics": {
                    "premium_product": True,  # Hand-woven silk
                    "unit_price_multiple": multiple,  # >5.0 (strong threshold)
                    "cash_to_itc_ratio": 0.31,
                    "long_establishment": True,
                    "corroboration_rule_saves_it": True,
                },
                "mock_unit_price": benchmark["median"] * multiple,
                "benchmark_median": benchmark["median"],
            })
        
        return entities
    
    def _generate_n5_industrial_estate(self, count: int) -> List[Dict[str, Any]]:
        """N5 - Real shared industrial estate (large adequate footprint)."""
        entities = []
        
        for i in range(count):
            entities.append({
                "type": "n5_industrial_estate",
                "gstin": f"N5IND{i:04d}",
                "legal_name": f"Industrial Estate Unit {i+1}",
                "pan": f"ABC12{i}D5Z5",
                "constitution": "llp",
                "registration_date": date.today() - timedelta(days=600),
                "declared_role": "manufacturer",
                "declared_hsn": ["540792"],
                "hard_negative": "n5_shared_large_footprint",
                "characteristics": {
                    "shared_location": True,
                    "adequate_footprint_m2": 12000,  # Large industrial estate
                    "clears_d2a_d3": True,
                    "industrial_zone": True,
                }
            })
        
        return entities
    
    def _generate_n6_unresolvable_address(self, count: int) -> List[Dict[str, Any]]:
        """N6 - Honest firm whose address simply cannot be geocoded."""
        entities = []
        
        for i in range(count):
            entities.append({
                "type": "n6_unresolvable_address",
                "gstin": f"N6UNRS{i:04d}",
                "legal_name": f"Clearance Case {i+1}",
                "pan": f"EFGHI{j}K6Z5",
                "constitution": "proprietorship",
                "registration_date": date.today() - timedelta(days=350),
                "declared_role": "trader",
                "declared_hsn": ["610910"],
                "hard_negative": "n6_address_unresolvable",
                "characteristics": {
                    "geocode_tier": "unresolved",
                    "field_verification_required": True,
                    "cleared_by_geocode_gate": True,
                }
            })
        
        return entities
    
    def _generate_clean_entities(self, count: int, district: str) -> List[Dict[str, Any]]:
        """Generate legitimate clean entities with normal business patterns."""
        entities = []
        
        for i in range(count):
            entities.append({
                "type": "clean_legitimate",
                "gstin": f"CLEAN{i:04d}",
                "legal_name": f"Genuine Business {i+1}",
                "pan": f"JKLMO{i}N7Z5",
                "constitution": random.choice(["private_ltd", "proprietorship", "partnership"]),
                "registration_date": date.today() - timedelta(days=random.randint(200, 1500)),
                "declared_role": random.choice(["manufacturer", "trader", "warehouse"]),
                "declared_hsn": random.choice([["540792"], ["610910"], ["520831"]]),
                "is_clean": True,
            })
        
        return entities
    
    def generate_invoice_lines(self, entities: List[Dict[str, Any]], quarters: int = 6):
        """
        Generate invoice lines for all entities.
        
        Creates realistic invoices with appropriate price variations based on entity type.
        """
        self.invoices = []
        quarter_length = 90  # days
        
        for entity in entities:
            gstin = entity["gstin"]
            hsn = entity["declared_hsn"][0]
            benchmark = self.hsn_benchmarks.get(hsn, {"median": 100})
            
            # Determine period
            for q in range(quarters):
                issue_date = date.today() - timedelta(days=quarter_length * (q + 1))
                
                if entity["type"].startswith("p2"):
                    # Over-invoiced - use inflated price
                    unit_price = entity.get("mock_unit_price", benchmark["median"] * 25)
                elif entity["type"].startswith("n4"):
                    # Premium - use higher but legitimate price
                    unit_price = entity.get("mock_unit_price", benchmark["median"] * 10)
                else:
                    # Normal prices
                    variation = random.gauss(1, 0.15)  # ±15% variation
                    unit_price = benchmark["median"] * max(0.5, variation)
                
                quantity_kg = random.uniform(100, 1000)
                taxable_value = round(unit_price * quantity_kg, 2)
                
                self.invoices.append({
                    "supplier_gstin": gstin,
                    "recipient_gstin": f"REC{random.randint(1000, 9999):04d}",
                    "document_date": issue_date,
                    "hsn": hsn,
                    "quantity_kg": quantity_kg,
                    "taxable_value": taxable_value,
                    "unit_price": unit_price,
                    "supply_type": random.choice(["export", "domestic"]),
                })
    
    def generate_refund_claims(self, entities: List[Dict[str, Any]]):
        """Generate refund claims for exporters."""
        self.refund_claims = []
        
        for entity in entities:
            if entity["declared_role"] == "manufacturer" and random.random() > 0.5:
                # Generate refund claim
                amount = random.uniform(50_00_000, 5_00_00_000)  # ₹50 lakh to ₹5 crore
                
                self.refund_claims.append({
                    "gstin": entity["gstin"],
                    "amount_claimed": round(amount, 2),
                    "route": "zero_rated_export",
                    "claim_id": str(uuid4()),
                })
    
    def export_json(self, output_dir: str = "./data"):
        """Export generated data to JSON files."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        with open(f"{output_dir}/entities.json", "w") as f:
            json.dump(self.entities, f, indent=2, default=str)
        
        with open(f"{output_dir}/invoices.json", "w") as f:
            json.dump(self.invoices, f, indent=2, default=str)
        
        with open(f"{output_dir}/refund_claims.json", "w") as f:
            json.dump(self.refund_claims, f, indent=2, default=str)
        
        print(f"\nExported to {output_dir}/")
        print(f"  - entities.json: {len(self.entities)} records")
        print(f"  - invoices.json: {len(self.invoices)} records")
        print(f"  - refund_claims.json: {len(self.refund_claims)} records")
    
    def print_summary(self):
        """Print summary statistics."""
        print("\n=== Synthetic Data Summary ===")
        print(f"Total entities: {len(self.entities)}")
        
        type_counts = {}
        for entity in self.entities:
            etype = entity["type"]
            type_counts[etype] = type_counts.get(etype, 0) + 1
        
        print("\nBy pattern:")
        for etype, count in sorted(type_counts.items()):
            print(f"  {etype}: {count}")
        
        print(f"\nTotal invoices: {len(self.invoices)}")
        print(f"Refund claims: {len(self.refund_claims)}")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic GST data for PACE prototype")
    parser.add_argument("--entities", type=int, default=DEFAULT_ENTITIES, help="Number of entities to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--district", type=str, default="Surat", help="Primary district")
    parser.add_argument("--output", type=str, default="./data", help="Output directory")
    
    args = parser.parse_args()
    
    generator = SyntheticDataGenerator(seed=args.seed)
    generator.generate_entities(args.entities, args.district)
    generator.generate_invoice_lines(generator.entities)
    generator.generate_refund_claims(generator.entities)
    generator.export_json(args.output)
    generator.print_summary()


if __name__ == "__main__":
    main()
