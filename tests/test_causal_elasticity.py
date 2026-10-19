"""
Unit Tests for Advancement 3: Causal Inference & Price Endogeneity Correction via 2SLS
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
import numpy as np
import pandas as pd
from src.forecasting.causal_elasticity import CausalElasticityEstimator

@pytest.fixture
def synthetic_endogenous_panel():
    # Simulate a realistic scenario where merchants raise prices when demand spikes (Q4), creating endogeneity
    np.random.seed(42)
    n = 60
    # True causal elasticity = -1.8
    # Cost instrument (exogenous supply shock)
    cost_instrument = np.random.uniform(2.0, 5.0, size=n)
    is_q4 = np.array([1 if i % 12 >= 9 else 0 for i in range(n)])
    
    # Endogenous price: depends on cost instrument + demand spike
    log_price = 0.5 * np.log(cost_instrument) + 0.3 * is_q4 + np.random.normal(0, 0.05, size=n)
    price = np.exp(log_price)
    
    # True demand: -1.8 * log(price) + seasonal spike + noise
    log_demand = 5.0 - 1.8 * log_price + 0.8 * is_q4 + np.random.normal(0, 0.1, size=n)
    demand = np.exp(log_demand)
    
    df = pd.DataFrame({
        "Weekly_Demand": demand,
        "Avg_Price": price,
        "Lag_1_Price": pd.Series(price).shift(1).fillna(price[0]),
        "Is_Q4": is_q4
    })
    return df

def test_first_stage_instrument_strength(synthetic_endogenous_panel):
    estimator = CausalElasticityEstimator()
    res = estimator.estimate_2sls_elasticity(synthetic_endogenous_panel)
    
    assert res["status"] == "success"
    assert res["first_stage_f_stat"] >= 10.0 # Stock-Yogo instrument relevance threshold
    assert "Strong" in res["instrument_strength"]

def test_causal_elasticity_negative_slope(synthetic_endogenous_panel):
    estimator = CausalElasticityEstimator()
    res = estimator.estimate_2sls_elasticity(synthetic_endogenous_panel)
    
    # Causal elasticity must be negative and recover downward demand response
    assert res["causal_2sls_elasticity"] < 0.0
    assert -3.0 <= res["causal_2sls_elasticity"] <= -0.5

def test_insufficient_data_fallback():
    # Create small 5-row dataframe
    df_small = pd.DataFrame({
        "Weekly_Demand": [10, 20, 15, 30, 25],
        "Avg_Price": [2.0, 2.5, 2.2, 2.8, 2.4],
        "Lag_1_Price": [2.0, 2.0, 2.5, 2.2, 2.8],
        "Is_Q4": [0, 0, 0, 1, 1]
    })
    estimator = CausalElasticityEstimator()
    res = estimator.estimate_2sls_elasticity(df_small)
    assert res["status"] == "insufficient_data"
    assert res["causal_2sls_elasticity"] == -1.45
