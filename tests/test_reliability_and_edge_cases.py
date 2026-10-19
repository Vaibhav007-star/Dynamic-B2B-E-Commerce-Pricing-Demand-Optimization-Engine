"""
Comprehensive Edge-Case, Robustness, and Reliability Tests
Validates non-negative constraints, fallback behaviors, zero demand handling, and pricing safety floors.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
import numpy as np
import pandas as pd

from src.optimization.price_optimizer import DynamicPriceOptimizer
from src.api.service import PricingService
from src.api.schemas import ForecastRequest

@pytest.fixture
def optimizer():
    return DynamicPriceOptimizer(
        min_gross_margin_pct=15.0,
        max_price_change_pct=20.0,
        default_elasticity=-1.45
    )

def test_zero_demand_handling(optimizer):
    """When baseline demand is 0, optimizer must safely return 0 revenue and 0 profit without error."""
    rec = optimizer.optimize_sku(
        sku="ZERO_DEMAND_SKU",
        description="Out of Season Item",
        base_price=10.0,
        unit_cost=6.0,
        base_demand=0.0
    )
    assert rec["expected_demand"] == 0.0
    assert rec["expected_revenue"] == 0.0
    assert rec["expected_profit"] == 0.0
    assert rec["recommended_price"] >= 6.0 * 1.15

def test_negative_or_zero_base_price(optimizer):
    """When base price is <= 0, optimizer must trigger safe fallback."""
    rec = optimizer.optimize_sku(
        sku="INVALID_PRICE_SKU",
        description="Corrupt SKU",
        base_price=0.0,
        unit_cost=5.0,
        base_demand=50.0
    )
    assert rec["recommended_price"] == 0.0
    assert "Invalid base pricing" in rec["rationale"]

def test_price_never_below_cost_floor(optimizer):
    """Under no circumstance can recommended price breach the unit cost floor."""
    # Test across 50 simulated random products
    rng = np.random.RandomState(42)
    for i in range(50):
        cost = round(rng.uniform(1.0, 50.0), 2)
        price = round(cost * rng.uniform(0.5, 2.0), 2) # Some prices start below cost
        demand = round(rng.uniform(1.0, 500.0), 1)
        
        rec = optimizer.optimize_sku(
            sku=f"RANDOM_SKU_{i}",
            description="Random Test SKU",
            base_price=price,
            unit_cost=cost,
            base_demand=demand
        )
        assert rec["recommended_price"] >= cost, f"Price {rec['recommended_price']} is below cost {cost}"
        assert rec["expected_profit"] >= -1e-5, f"Profit {rec['expected_profit']} is negative"

def test_unseen_sku_elasticity_fallback(optimizer):
    """An SKU not present in the fitted elasticity map must gracefully fallback to the portfolio default."""
    assert "UNKNOWN_SKU_9999" not in optimizer.sku_elasticities
    rec = optimizer.optimize_sku(
        sku="UNKNOWN_SKU_9999",
        description="New Product",
        base_price=20.0,
        unit_cost=12.0,
        base_demand=30.0
    )
    assert rec["elasticity"] == optimizer.default_elasticity
    assert rec["recommended_price"] >= 12.0 * 1.15

def test_forecasting_negative_clamping():
    """Demand forecaster must reject negative input lags and always output non-negative predictions."""
    service = PricingService()
    
    # 1. Pydantic must reject negative lag values
    with pytest.raises(Exception):
        ForecastRequest(
            sku="EXTREME_LAG_SKU",
            avg_price=100.0,
            rolling_mean_4w=-50.0 # Invalid negative
        )
        
    # 2. Valid zero-demand edge case must produce non-negative output
    req_valid = ForecastRequest(
        sku="ZERO_LAG_SKU",
        avg_price=10.0,
        lag_1_demand=0.0,
        lag_2_demand=0.0,
        lag_4_demand=0.0,
        lag_8_demand=0.0,
        rolling_mean_4w=0.0
    )
    res = service.forecast_demand(req_valid)
    assert res.predicted_weekly_demand >= 0.0

def test_dashboard_feeds_integrity():
    """Verify generated Tableau CSV feeds exist, are non-empty, and contain required schema."""
    exec_csv = Path("dashboard/tableau_data/tableau_executive_overview.csv")
    rec_csv = Path("dashboard/tableau_data/tableau_pricing_recommendations.csv")
    
    assert exec_csv.exists(), "tableau_executive_overview.csv is missing"
    assert rec_csv.exists(), "tableau_pricing_recommendations.csv is missing"
    
    df_exec = pd.read_csv(exec_csv)
    df_rec = pd.read_csv(rec_csv)
    
    assert len(df_exec) == 1
    assert len(df_rec) >= 3000
    assert "Gross_Profit_Uplift_GBP" in df_exec.columns
    assert "recommended_price" in df_rec.columns
    assert (df_rec["recommended_price"] < df_rec["unit_cost"]).sum() == 0
