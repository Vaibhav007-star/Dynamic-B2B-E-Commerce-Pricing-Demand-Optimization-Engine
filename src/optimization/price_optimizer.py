"""
Dynamic B2B Pricing Optimization Engine
Estimates product-level price elasticity of demand, evaluates candidate price grids
under business margin and volatility constraints, and selects the gross-profit-maximizing price.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
import numpy as np
import pandas as pd

class DynamicPriceOptimizer:
    def __init__(
        self,
        min_gross_margin_pct: float = 15.0,
        max_price_change_pct: float = 20.0,
        default_elasticity: float = -1.45,
        grid_steps: int = 21
    ):
        self.min_gross_margin_pct = min_gross_margin_pct
        self.max_price_change_pct = max_price_change_pct
        self.default_elasticity = default_elasticity
        self.grid_steps = grid_steps
        self.sku_elasticities = {}
        
    def fit_elasticities(self, panel_df: pd.DataFrame):
        """
        Estimates empirical price elasticity per SKU using log-log regression:
        ln(Demand + 1) = alpha + beta * ln(Price)
        Shrinks noisy or positive slopes to default economic elasticity.
        """
        print("Fitting SKU price elasticity models from historical price-demand variations...")
        grouped = panel_df.groupby("StockCode")
        fitted_count = 0
        
        for sku, group in grouped:
            valid = group[(group["Weekly_Demand"] > 0) & (group["Avg_Price"] > 0)].copy()
            if len(valid) >= 6 and valid["Avg_Price"].std() > 0.05:
                # Log-log OLS
                log_p = np.log(valid["Avg_Price"].values)
                log_q = np.log(valid["Weekly_Demand"].values)
                var_p = np.var(log_p)
                if var_p > 1e-5:
                    cov_pq = np.cov(log_p, log_q)[0, 1]
                    beta = cov_pq / var_p
                    # Economic constraint: Demand curve must be downward sloping (-3.5 <= beta <= -0.2)
                    if -3.5 <= beta <= -0.2:
                        self.sku_elasticities[sku] = round(float(beta), 3)
                        fitted_count += 1
                        continue
            # Empirical Bayesian shrinkage to default portfolio elasticity
            self.sku_elasticities[sku] = self.default_elasticity

        print(f"Fitted elasticity profiles for {len(self.sku_elasticities):,} SKUs ({fitted_count:,} with direct empirical variance).")

    def get_elasticity(self, sku: str) -> float:
        return self.sku_elasticities.get(sku, self.default_elasticity)

    def optimize_sku(
        self,
        sku: str,
        description: str,
        base_price: float,
        unit_cost: float,
        base_demand: float
    ) -> dict:
        """
        Generates candidate prices within constraints, computes expected demand and gross profit,
        and selects the gross-profit-optimal price.
        """
        if base_price <= 0 or unit_cost <= 0:
            return {
                "sku": sku,
                "description": description,
                "base_price": base_price,
                "recommended_price": base_price,
                "price_change_pct": 0.0,
                "unit_cost": unit_cost,
                "elasticity": self.default_elasticity,
                "baseline_demand": max(0.0, base_demand),
                "expected_demand": max(0.0, base_demand),
                "baseline_revenue": 0.0,
                "expected_revenue": 0.0,
                "baseline_profit": 0.0,
                "expected_profit": 0.0,
                "expected_margin_pct": 0.0,
                "rationale": "Invalid base pricing or cost parameters."
            }

        elasticity = self.get_elasticity(sku)
        
        # Hard safety floor: Price can NEVER be below unit cost + min margin
        min_allowed_by_margin = unit_cost * (1.0 + self.min_gross_margin_pct / 100.0)
        
        # Volatility bounds relative to base_price
        min_allowed_by_change = base_price * (1.0 - self.max_price_change_pct / 100.0)
        max_allowed_by_change = base_price * (1.0 + self.max_price_change_pct / 100.0)
        
        # Lower bound is strictly bounded by the cost margin floor
        lower_bound = max(min_allowed_by_change, min_allowed_by_margin)
        upper_bound = max(max_allowed_by_change, lower_bound * 1.05)

        candidate_prices = np.linspace(lower_bound, upper_bound, self.grid_steps)
        
        # Baseline calculations at existing price
        base_profit = (base_price - unit_cost) * base_demand
        base_revenue = base_price * base_demand
        
        # Initialize optimal selection with the lowest feasible compliant candidate price
        best_price = candidate_prices[0]
        price_ratio_init = best_price / base_price
        best_demand = max(0.0, base_demand * (price_ratio_init ** elasticity))
        best_profit = (best_price - unit_cost) * best_demand
        best_revenue = best_price * best_demand
        
        # Grid evaluation
        for p_cand in candidate_prices:
            # Constant elasticity demand response: Q(P) = Q0 * (P / P0)^epsilon
            price_ratio = p_cand / base_price
            exp_demand = max(0.0, base_demand * (price_ratio ** elasticity))
            exp_profit = (p_cand - unit_cost) * exp_demand
            exp_revenue = p_cand * exp_demand
            
            if exp_profit > best_profit:
                best_profit = exp_profit
                best_price = p_cand
                best_demand = exp_demand
                best_revenue = exp_revenue

        price_delta_pct = ((best_price - base_price) / base_price) * 100.0
        exp_margin_pct = (best_profit / best_revenue * 100.0) if best_revenue > 0 else 0.0

        # Rationale formulation
        if abs(price_delta_pct) < 0.5:
            rationale = "Current price is already at the optimal gross-profit balance point."
        elif price_delta_pct > 0:
            if elasticity > -1.0:
                rationale = f"Inelastic demand (elasticity={elasticity:.2f}): Price uplift captures higher margin with minimal volume attrition."
            else:
                rationale = f"Margin expansion (elasticity={elasticity:.2f}): Price uplift optimizes gross profit per unit over volume decline."
        else:
            rationale = f"Elastic demand (elasticity={elasticity:.2f}): Moderate price reduction stimulates volume uplift, expanding overall gross profit."

        return {
            "sku": sku,
            "description": description,
            "base_price": round(base_price, 2),
            "recommended_price": round(best_price, 2),
            "price_change_pct": round(price_delta_pct, 2),
            "unit_cost": round(unit_cost, 2),
            "elasticity": round(elasticity, 2),
            "baseline_demand": round(base_demand, 1),
            "expected_demand": round(best_demand, 1),
            "baseline_revenue": round(base_revenue, 2),
            "expected_revenue": round(best_revenue, 2),
            "baseline_profit": round(base_profit, 2),
            "expected_profit": round(best_profit, 2),
            "expected_margin_pct": round(exp_margin_pct, 2),
            "rationale": rationale
        }

if __name__ == "__main__":
    optimizer = DynamicPriceOptimizer()
    sample_res = optimizer.optimize_sku(
        sku="85123A",
        description="WHITE HANGING HEART T-LIGHT HOLDER",
        base_price=2.95,
        unit_cost=1.92,
        base_demand=120.0
    )
    print("Sample Single SKU Optimization Result:")
    print(json.dumps(sample_res, indent=4))
