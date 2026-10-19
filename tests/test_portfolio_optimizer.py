"""
Unit Tests for Advancement 2: Operations Research Portfolio Cannibalization Optimizer
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
import numpy as np
from src.optimization.portfolio_optimizer import PortfolioCannibalizationOptimizer

@pytest.fixture
def sample_bundle():
    return [
        {"sku": "SKU_A", "name": "Premium Cake Stand 3T", "base_price": 12.00, "unit_cost": 7.00, "base_demand": 100.0, "own_elasticity": -1.2},
        {"sku": "SKU_B", "name": "Standard Cake Stand 2T", "base_price": 8.00, "unit_cost": 4.50, "base_demand": 180.0, "own_elasticity": -1.7},
        {"sku": "SKU_C", "name": "Accessory Serving Plate", "base_price": 3.00, "unit_cost": 1.50, "base_demand": 300.0, "own_elasticity": -1.0}
    ]

def test_solver_convergence_and_uplift(sample_bundle):
    opt = PortfolioCannibalizationOptimizer(target_portfolio_margin_pct=40.0)
    res = opt.optimize_portfolio_bundle(sample_bundle)
    
    assert res["solver_converged"] is True
    assert res["portfolio_optimized_profit"] >= res["portfolio_baseline_profit"]
    assert res["profit_uplift_pct"] >= 0.0
    assert len(res["products"]) == 3

def test_portfolio_margin_constraint_satisfaction(sample_bundle):
    # Set ambitious portfolio target margin
    target_margin = 48.0
    opt = PortfolioCannibalizationOptimizer(target_portfolio_margin_pct=target_margin)
    res = opt.optimize_portfolio_bundle(sample_bundle)
    
    assert res["realized_portfolio_margin_pct"] >= target_margin - 0.1 # Within solver tolerance

def test_cross_elasticity_cannibalization_tradeoff(sample_bundle):
    # When cross-elasticity is high (substitutes exist), increasing price on SKU_A shifts demand to SKU_B
    E_matrix = np.array([
        [-1.2,  0.4,  0.1],
        [ 0.3, -1.7,  0.1],
        [ 0.1,  0.1, -1.0]
    ])
    opt = PortfolioCannibalizationOptimizer(target_portfolio_margin_pct=42.0)
    res = opt.optimize_portfolio_bundle(sample_bundle, cross_elasticity_matrix=E_matrix)
    
    assert res["solver_converged"] is True
    for p in res["products"]:
        # Verify boundary constraints respected: price >= cost * 1.15
        assert p["optimized_price"] >= p["unit_cost"] * 1.15
        # Verify within 20% volatility
        assert abs(p["price_change_pct"]) <= 20.0 + 1e-3
