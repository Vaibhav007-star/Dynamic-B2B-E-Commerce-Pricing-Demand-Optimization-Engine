"""
Unit Tests for Advancement 1: B2B Multi-Tier Volume Pricing & Customer Segmentation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
import pandas as pd
from src.optimization.b2b_tiered_pricing import B2BTieredPricingEngine

@pytest.fixture(scope="module")
def engine():
    eng = B2BTieredPricingEngine(n_clusters=3, random_state=42)
    eng.fit_customer_segments()
    return eng

def test_customer_segmentation_clustering(engine):
    assert len(engine.segment_profiles) == 3
    assert len(engine.customer_segments) > 1000
    segment_names = [p["Segment_Name"] for p in engine.segment_profiles]
    assert "Enterprise Wholesaler" in segment_names
    assert "Trade / Boutique Account" in segment_names
    assert "Spot Retail Buyer" in segment_names

def test_volume_tier_monotonic_discounting(engine):
    # Test for normal commodity product
    schedule = engine.calculate_volume_tier_schedule(
        base_recommended_price=10.00,
        unit_cost=5.00,
        elasticity=-1.5,
        min_gross_margin_pct=15.0
    )
    p1 = schedule["tier_1_spot"]["unit_price"]
    p2 = schedule["tier_2_case"]["unit_price"]
    p3 = schedule["tier_3_bulk"]["unit_price"]
    
    assert p1 >= p2 >= p3, f"Expected monotonic price drops: {p1} >= {p2} >= {p3}"
    assert schedule["tier_2_case"]["discount_pct"] > 0.0
    assert schedule["tier_3_bulk"]["discount_pct"] >= schedule["tier_2_case"]["discount_pct"]

def test_volume_tier_cost_floor_compliance(engine):
    # Test product where base price is close to unit cost
    schedule = engine.calculate_volume_tier_schedule(
        base_recommended_price=5.10,
        unit_cost=5.00, # Cost floor = 5.00 * 1.15 = 5.75
        elasticity=-2.5,
        min_gross_margin_pct=15.0
    )
    floor = schedule["governance"]["floor_price"]
    assert schedule["tier_1_spot"]["unit_price"] >= floor
    assert schedule["tier_2_case"]["unit_price"] >= floor
    assert schedule["tier_3_bulk"]["unit_price"] >= floor
    assert schedule["governance"]["cost_floor_protected"] is True

def test_customer_quote_generation(engine):
    # Retrieve an Enterprise Wholesaler customer ID
    wholesaler_id = next(
        cid for cid, info in engine.customer_segments.items() 
        if info["Segment_Name"] == "Enterprise Wholesaler"
    )
    
    # Large bulk order
    quote = engine.get_customer_quote(
        customer_id=wholesaler_id,
        sku="85123A",
        base_recommended_price=3.54,
        unit_cost=1.92,
        quantity=100 # Bulk tier
    )
    assert quote["segment_name"] == "Enterprise Wholesaler"
    assert quote["applied_tier"] == "50+ units (Bulk Pallet)"
    assert quote["final_quoted_unit_price"] < 3.54
    assert quote["margin_floor_protected"] is True
    assert quote["total_gross_profit"] > 0
