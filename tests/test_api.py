"""
Automated Integration and Unit Tests for FastAPI Dynamic Pricing Engine
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "products_count" in data
    assert data["products_count"] > 0

def test_get_products_pagination():
    response = client.get("/products?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["products"]) == 10
    first = data["products"][0]
    assert "sku" in first
    assert "base_price" in first
    assert "unit_cost" in first

def test_forecast_demand_valid():
    payload = {
        "sku": "85123A",
        "avg_price": 2.95,
        "lag_1_demand": 110.0,
        "lag_2_demand": 105.0,
        "lag_4_demand": 115.0,
        "lag_8_demand": 120.0,
        "rolling_mean_4w": 112.5,
        "rolling_mean_8w": 114.0,
        "rolling_std_4w": 8.2,
        "month": 10,
        "quarter": 4,
        "week_of_year": 42,
        "is_q4": 1
    }
    response = client.post("/forecast", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sku"] == "85123A"
    assert data["predicted_weekly_demand"] >= 0

def test_forecast_demand_invalid_price():
    payload = {
        "sku": "85123A",
        "avg_price": -5.0, # Invalid negative price
        "rolling_mean_4w": 50.0
    }
    response = client.post("/forecast", json=payload)
    assert response.status_code == 422 # Unprocessable Entity validation error

def test_pricing_recommend_valid():
    payload = {
        "sku": "85123A",
        "description": "WHITE HANGING HEART T-LIGHT HOLDER",
        "base_price": 2.95,
        "unit_cost": 1.92,
        "base_demand": 120.0,
        "min_gross_margin_pct": 15.0,
        "max_price_change_pct": 20.0
    }
    response = client.post("/pricing/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sku"] == "85123A"
    assert data["recommended_price"] >= data["unit_cost"] # Safety check
    assert data["expected_profit"] >= data["baseline_profit"]
    assert "rationale" in data

def test_pricing_recommend_cost_safety():
    # Test case where base price is below unit cost
    payload = {
        "sku": "TEST_LOSS_LEADER",
        "base_price": 1.00,
        "unit_cost": 1.50, # Cost exceeds base price
        "base_demand": 100.0,
        "min_gross_margin_pct": 15.0
    }
    response = client.post("/pricing/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Recommended price must be pushed up to at least cost + 15% margin
    assert data["recommended_price"] >= 1.50 * 1.15

def test_pricing_recommend_invalid_cost():
    payload = {
        "sku": "INVALID_COST",
        "base_price": 5.0,
        "unit_cost": -2.0, # Invalid cost
        "base_demand": 10.0
    }
    response = client.post("/pricing/recommend", json=payload)
    assert response.status_code == 422

def test_get_pricing_results():
    response = client.get("/pricing/results?limit=15")
    assert response.status_code == 200
    data = response.json()
    assert data["total_recommendations"] > 0
    assert len(data["results"]) == 15
    for item in data["results"]:
        assert item["recommended_price"] >= item["unit_cost"]

def test_get_business_impact():
    response = client.get("/business/impact")
    assert response.status_code == 200
    data = response.json()
    assert data["products_analyzed"] > 0
    assert data["gross_profit_change"] > 0
    assert data["relative_gross_profit_improvement_pct"] > 0
    assert data["safety_checks"]["prices_below_cost"] == 0
