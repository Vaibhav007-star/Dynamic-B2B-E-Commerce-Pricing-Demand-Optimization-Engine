"""
Business Logic & Service Layer for FastAPI
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
import joblib
import pandas as pd
import numpy as np

from src.optimization.price_optimizer import DynamicPriceOptimizer
from src.api.schemas import (
    ProductItem, ProductListResponse,
    ForecastRequest, ForecastResponse,
    PricingRecommendRequest, PricingRecommendResponse,
    PricingResultsResponse, BusinessImpactResponse
)

MODEL_PATH = Path("models/demand_forecaster_best.joblib")
PANEL_PATH = Path("data/processed/demand_weekly_panel.parquet")
TRANSACTIONS_PATH = Path("data/processed/b2b_transactions_clean.parquet")
RECOMMENDATIONS_PATH = Path("data/outputs/pricing_recommendations.parquet")
IMPACT_JSON_PATH = Path("data/outputs/business_impact_summary.json")

class PricingService:
    def __init__(self):
        self.forecaster_bundle = None
        self.optimizer = None
        self.products_df = None
        self.recommendations_df = None
        self.impact_summary = None
        self.load_artifacts()

    def load_artifacts(self):
        # 1. Load trained forecaster
        if MODEL_PATH.exists():
            self.forecaster_bundle = joblib.load(MODEL_PATH)
            print("Loaded demand forecaster bundle.")
        
        # 2. Load panel & pre-fit optimizer
        if PANEL_PATH.exists():
            panel = pd.read_parquet(PANEL_PATH)
            self.optimizer = DynamicPriceOptimizer()
            self.optimizer.fit_elasticities(panel)
            
            # Prepare fast product lookup
            tx_unit_cost = {}
            if TRANSACTIONS_PATH.exists():
                tx_df = pd.read_parquet(TRANSACTIONS_PATH, columns=["StockCode", "Unit_Cost"])
                tx_unit_cost = tx_df.groupby("StockCode")["Unit_Cost"].first().to_dict()
                
            latest = panel.sort_values("Week_Start").groupby("StockCode").last().reset_index()
            latest["unit_cost"] = latest["StockCode"].map(lambda sc: tx_unit_cost.get(sc, round(float(latest.loc[latest["StockCode"]==sc, "Avg_Price"].values[0]) * 0.65, 2)))
            latest["Description"] = latest["Description"].fillna("Product " + latest["StockCode"].astype(str))
            self.products_df = latest
            print(f"Loaded {len(self.products_df):,} products into memory.")

        # 3. Load pre-calculated recommendations
        if RECOMMENDATIONS_PATH.exists():
            self.recommendations_df = pd.read_parquet(RECOMMENDATIONS_PATH)
            print(f"Loaded {len(self.recommendations_df):,} cached pricing recommendations.")

        # 4. Load impact summary
        if IMPACT_JSON_PATH.exists():
            with open(IMPACT_JSON_PATH, "r") as f:
                self.impact_summary = json.load(f)

    def get_products(self, page: int = 1, page_size: int = 50) -> ProductListResponse:
        if self.products_df is None or len(self.products_df) == 0:
            return ProductListResponse(total_products=0, page=page, page_size=page_size, products=[])
        
        total = len(self.products_df)
        start = (page - 1) * page_size
        end = start + page_size
        sub = self.products_df.iloc[start:end]
        
        items = [
            ProductItem(
                sku=str(row["StockCode"]),
                description=str(row.get("Description", "Product " + str(row["StockCode"]))),
                base_price=round(float(row.get("Avg_Price", 1.0)), 2),
                unit_cost=round(float(row.get("unit_cost", 0.65)), 2),
                current_demand=round(float(row.get("Weekly_Demand", 0.0)), 1)
            )
            for _, row in sub.iterrows()
        ]
        return ProductListResponse(total_products=total, page=page, page_size=page_size, products=items)

    def forecast_demand(self, req: ForecastRequest) -> ForecastResponse:
        model_name = self.forecaster_bundle.get("model_name", "Historical_Baseline") if self.forecaster_bundle else "Historical_Baseline"
        model = self.forecaster_bundle.get("model") if self.forecaster_bundle else None
        
        if model is None or model_name == "Historical_Baseline":
            pred = max(0.0, float(req.rolling_mean_4w))
        else:
            feature_cols = self.forecaster_bundle["feature_cols"]
            input_dict = {
                "Lag_1_Demand": req.lag_1_demand,
                "Lag_2_Demand": req.lag_2_demand,
                "Lag_4_Demand": req.lag_4_demand,
                "Lag_8_Demand": req.lag_8_demand,
                "Rolling_Mean_4w": req.rolling_mean_4w,
                "Rolling_Mean_8w": req.rolling_mean_8w,
                "Rolling_Std_4w": req.rolling_std_4w,
                "Avg_Price": req.avg_price,
                "Lag_1_Price": req.avg_price,
                "Price_Ratio_to_Lag": 1.0,
                "Month": req.month,
                "Quarter": req.quarter,
                "Week_Of_Year": req.week_of_year,
                "Is_Q4": req.is_q4
            }
            x_in = pd.DataFrame([input_dict])[feature_cols]
            pred = float(np.clip(model.predict(x_in)[0], 0, None))
            
        return ForecastResponse(
            sku=req.sku,
            predicted_weekly_demand=round(pred, 1),
            model_used=model_name
        )

    def recommend_price(self, req: PricingRecommendRequest) -> PricingRecommendResponse:
        if self.optimizer is None:
            self.optimizer = DynamicPriceOptimizer()
        
        # Override optimizer parameters if passed
        opt = DynamicPriceOptimizer(
            min_gross_margin_pct=req.min_gross_margin_pct or 15.0,
            max_price_change_pct=req.max_price_change_pct or 20.0,
            default_elasticity=self.optimizer.default_elasticity
        )
        opt.sku_elasticities = self.optimizer.sku_elasticities
        
        desc = req.description or f"Product {req.sku}"
        res = opt.optimize_sku(
            sku=req.sku,
            description=desc,
            base_price=req.base_price,
            unit_cost=req.unit_cost,
            base_demand=req.base_demand
        )
        return PricingRecommendResponse(**res)

    def get_pricing_results(self, limit: int = 100) -> PricingResultsResponse:
        if self.recommendations_df is None or len(self.recommendations_df) == 0:
            return PricingResultsResponse(total_recommendations=0, results=[])
        
        sub = self.recommendations_df.head(limit)
        results = [
            PricingRecommendResponse(
                sku=str(row["sku"]),
                description=str(row.get("description", "SKU " + str(row["sku"]))),
                base_price=float(row["base_price"]),
                recommended_price=float(row["recommended_price"]),
                price_change_pct=float(row["price_change_pct"]),
                unit_cost=float(row["unit_cost"]),
                elasticity=float(row["elasticity"]),
                baseline_demand=float(row["baseline_demand"]),
                expected_demand=float(row["expected_demand"]),
                baseline_revenue=float(row["baseline_revenue"]),
                expected_revenue=float(row["expected_revenue"]),
                baseline_profit=float(row["baseline_profit"]),
                expected_profit=float(row["expected_profit"]),
                expected_margin_pct=float(row["expected_margin_pct"]),
                rationale=str(row["rationale"])
            )
            for _, row in sub.iterrows()
        ]
        return PricingResultsResponse(total_recommendations=len(self.recommendations_df), results=results)

    def get_business_impact(self) -> BusinessImpactResponse:
        if self.impact_summary is None:
            raise ValueError("Business impact summary not found. Run business_impact.py first.")
        return BusinessImpactResponse(**self.impact_summary)

# Singleton instance
service = PricingService()
