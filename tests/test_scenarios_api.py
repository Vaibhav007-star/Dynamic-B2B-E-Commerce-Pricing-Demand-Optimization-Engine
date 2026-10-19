"""
Unit Tests for Advancement 4: Executive What-If War Gaming Scenarios Endpoint
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_baseline_scenario():
    response = client.post("/scenarios/simulate", json={"scenario_type": "baseline"})
    assert response.status_code == 200
    data = response.json()
    assert "Baseline" in data["scenario_name"]
    assert data["portfolio_profit"] > 200000.0
    assert data["portfolio_margin_pct"] >= 50.0
    assert data["profit_delta_vs_baseline_gbp"] > 0

def test_cost_inflation_scenario():
    response = client.post("/scenarios/simulate", json={
        "scenario_type": "cost_inflation",
        "cost_shock_pct": 10.0
    })
    assert response.status_code == 200
    data = response.json()
    assert "Inflation" in data["scenario_name"]
    assert "inelastic" in data["actionable_mitigation"].lower()
    assert data["portfolio_profit"] > 0

def test_competitor_war_scenario():
    response = client.post("/scenarios/simulate", json={
        "scenario_type": "competitor_war",
        "competitor_cut_pct": 8.0
    })
    assert response.status_code == 200
    data = response.json()
    assert "Competitor" in data["scenario_name"]
    assert "elastic" in data["actionable_mitigation"].lower()

def test_margin_mandate_scenario():
    response = client.post("/scenarios/simulate", json={
        "scenario_type": "margin_mandate",
        "target_margin_floor_pct": 55.0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["portfolio_margin_pct"] >= 55.0
    assert "55" in data["scenario_name"]
