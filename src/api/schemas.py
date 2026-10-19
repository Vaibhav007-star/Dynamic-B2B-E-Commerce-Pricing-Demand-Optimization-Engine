"""
Pydantic Schemas for FastAPI Dynamic Pricing & Forecasting Service
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "healthy"})
    version: str = Field(..., json_schema_extra={"example": "1.0.0"})
    model_loaded: bool = Field(..., json_schema_extra={"example": True})
    products_count: int = Field(..., json_schema_extra={"example": 3484})

class ProductItem(BaseModel):
    sku: str = Field(..., json_schema_extra={"example": "85123A"})
    description: str = Field(..., json_schema_extra={"example": "WHITE HANGING HEART T-LIGHT HOLDER"})
    base_price: float = Field(..., json_schema_extra={"example": 2.95})
    unit_cost: float = Field(..., json_schema_extra={"example": 1.92})
    current_demand: float = Field(..., json_schema_extra={"example": 120.0})

class ProductListResponse(BaseModel):
    total_products: int
    page: int
    page_size: int
    products: List[ProductItem]

class ForecastRequest(BaseModel):
    sku: str = Field(..., json_schema_extra={"example": "85123A"})
    avg_price: float = Field(..., gt=0, json_schema_extra={"example": 2.95})
    lag_1_demand: float = Field(0.0, ge=0, json_schema_extra={"example": 110.0})
    lag_2_demand: float = Field(0.0, ge=0, json_schema_extra={"example": 105.0})
    lag_4_demand: float = Field(0.0, ge=0, json_schema_extra={"example": 115.0})
    lag_8_demand: float = Field(0.0, ge=0, json_schema_extra={"example": 120.0})
    rolling_mean_4w: float = Field(0.0, ge=0, json_schema_extra={"example": 112.5})
    rolling_mean_8w: float = Field(0.0, ge=0, json_schema_extra={"example": 114.0})
    rolling_std_4w: float = Field(0.0, ge=0, json_schema_extra={"example": 8.2})
    month: int = Field(10, ge=1, le=12)
    quarter: int = Field(4, ge=1, le=4)
    week_of_year: int = Field(42, ge=1, le=53)
    is_q4: int = Field(1, ge=0, le=1)

class ForecastResponse(BaseModel):
    sku: str
    predicted_weekly_demand: float
    model_used: str

class PricingRecommendRequest(BaseModel):
    sku: str = Field(..., json_schema_extra={"example": "85123A"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "WHITE HANGING HEART T-LIGHT HOLDER"})
    base_price: float = Field(..., gt=0, json_schema_extra={"example": 2.95})
    unit_cost: float = Field(..., gt=0, json_schema_extra={"example": 1.92})
    base_demand: float = Field(..., ge=0, json_schema_extra={"example": 120.0})
    min_gross_margin_pct: Optional[float] = Field(15.0, ge=0.0, le=100.0)
    max_price_change_pct: Optional[float] = Field(20.0, ge=1.0, le=50.0)

    @field_validator("unit_cost")
    @classmethod
    def validate_cost_below_or_equal_to_margin(cls, v, values):
        if v <= 0:
            raise ValueError("unit_cost must be greater than zero")
        return v

class PricingRecommendResponse(BaseModel):
    sku: str
    description: str
    base_price: float
    recommended_price: float
    price_change_pct: float
    unit_cost: float
    elasticity: float
    baseline_demand: float
    expected_demand: float
    baseline_revenue: float
    expected_revenue: float
    baseline_profit: float
    expected_profit: float
    expected_margin_pct: float
    rationale: str

class PricingResultsResponse(BaseModel):
    total_recommendations: int
    results: List[PricingRecommendResponse]

class BusinessImpactResponse(BaseModel):
    products_analyzed: int
    total_baseline_revenue: float
    total_optimized_revenue: float
    revenue_change: float
    relative_revenue_change_pct: float
    total_baseline_gross_profit: float
    total_optimized_gross_profit: float
    gross_profit_change: float
    relative_gross_profit_improvement_pct: float
    baseline_gross_margin_pct: float
    optimized_gross_margin_pct: float
    baseline_units_demanded: float
    optimized_units_demanded: float
    price_actions: Dict[str, int]
    safety_checks: Dict[str, Any]

class ScenarioSimulateRequest(BaseModel):
    scenario_type: str = Field("baseline", json_schema_extra={"example": "cost_inflation"})
    cost_shock_pct: float = Field(0.0, json_schema_extra={"example": 10.0})
    competitor_cut_pct: float = Field(0.0, json_schema_extra={"example": 0.0})
    target_margin_floor_pct: float = Field(15.0, json_schema_extra={"example": 15.0})

class ScenarioSimulateResponse(BaseModel):
    scenario_name: str
    portfolio_revenue: float
    portfolio_profit: float
    portfolio_margin_pct: float
    profit_delta_vs_baseline_gbp: float
    profit_delta_vs_baseline_pct: float
    recommended_price_uplift_pct: float
    strategic_recommendation: str
    actionable_mitigation: str
