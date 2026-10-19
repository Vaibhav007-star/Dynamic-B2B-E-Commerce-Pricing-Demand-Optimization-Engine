"""
Advancement 2: Operations Research Portfolio Optimizer with Cross-Elasticity & Cannibalization
Formulates and solves a constrained non-linear mathematical optimization problem over a product portfolio
using SciPy SLSQP.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
import pandas as pd
from scipy.optimize import minimize

class PortfolioCannibalizationOptimizer:
    def __init__(self, target_portfolio_margin_pct: float = 52.0, max_price_delta_pct: float = 20.0):
        self.target_portfolio_margin_pct = target_portfolio_margin_pct
        self.max_price_delta_pct = max_price_delta_pct
        
    def optimize_portfolio_bundle(
        self,
        products: list[dict],
        cross_elasticity_matrix: np.ndarray = None
    ) -> dict:
        """
        products: list of dicts with keys:
            ['sku', 'name', 'base_price', 'unit_cost', 'base_demand', 'own_elasticity']
        cross_elasticity_matrix: NxN matrix where E[i,j] is the cross elasticity d(ln Qi) / d(ln Pj).
            Diagonal E[i,i] is own-price elasticity.
        """
        n = len(products)
        p0 = np.array([p["base_price"] for p in products], dtype=float)
        costs = np.array([p["unit_cost"] for p in products], dtype=float)
        q0 = np.array([p["base_demand"] for p in products], dtype=float)
        
        # Build elasticity matrix if not supplied
        if cross_elasticity_matrix is None:
            E = np.zeros((n, n), dtype=float)
            for i in range(n):
                E[i, i] = products[i].get("own_elasticity", -1.45)
                for j in range(n):
                    if i != j:
                        # Realistic wholesale substitute cross-elasticity (+0.15 to +0.35)
                        E[i, j] = 0.22
        else:
            E = np.array(cross_elasticity_matrix, dtype=float)
            
        # Bounds: [cost * 1.15, p0 * 1.20]
        bounds = []
        for i in range(n):
            lower = max(costs[i] * 1.15, p0[i] * (1.0 - self.max_price_delta_pct / 100.0))
            upper = max(p0[i] * (1.0 + self.max_price_delta_pct / 100.0), lower * 1.05)
            bounds.append((lower, upper))
            
        def demand_func(prices):
            # Price delta ratio (P - P0) / P0
            price_ratios = (prices - p0) / p0
            # Matrix vector product: E @ price_ratios gives fractional demand shift vector
            delta_q_ratio = E @ price_ratios
            q_opt = q0 * (1.0 + delta_q_ratio)
            return np.clip(q_opt, 0.0, None)
            
        # Objective: Maximize gross profit -> Minimize negative profit
        def objective(prices):
            q_current = demand_func(prices)
            total_profit = np.sum((prices - costs) * q_current)
            return -total_profit
            
        # Constraint: Portfolio Gross Margin >= Target Margin %
        def margin_constraint(prices):
            q_current = demand_func(prices)
            total_rev = np.sum(prices * q_current)
            total_gp = np.sum((prices - costs) * q_current)
            if total_rev <= 0:
                return 0.0
            actual_margin_pct = (total_gp / total_rev) * 100.0
            return actual_margin_pct - self.target_portfolio_margin_pct
            
        constraints = [
            {"type": "ineq", "fun": margin_constraint}
        ]
        
        # Initial guess = p0
        x0 = np.clip(p0, [b[0] for b in bounds], [b[1] for b in bounds])
        
        # Solve with SLSQP
        res = minimize(
            objective,
            x0=x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 200, "ftol": 1e-6}
        )
        
        p_opt = res.x if res.success else x0
        q_opt = demand_func(p_opt)
        
        # Calculate baseline vs joint optimal comparison
        base_profit = float(np.sum((p0 - costs) * q0))
        base_revenue = float(np.sum(p0 * q0))
        base_margin = (base_profit / base_revenue * 100.0) if base_revenue > 0 else 0.0
        
        opt_profit = float(np.sum((p_opt - costs) * q_opt))
        opt_revenue = float(np.sum(p_opt * q_opt))
        opt_margin = (opt_profit / opt_revenue * 100.0) if opt_revenue > 0 else 0.0
        
        sku_details = []
        for i in range(n):
            sku_details.append({
                "sku": products[i]["sku"],
                "name": products[i]["name"],
                "base_price": round(float(p0[i]), 2),
                "optimized_price": round(float(p_opt[i]), 2),
                "price_change_pct": round(float(((p_opt[i] - p0[i]) / p0[i]) * 100.0), 2),
                "unit_cost": round(float(costs[i]), 2),
                "baseline_demand": round(float(q0[i]), 1),
                "expected_demand": round(float(q_opt[i]), 1),
                "baseline_profit": round(float((p0[i] - costs[i]) * q0[i]), 2),
                "expected_profit": round(float((p_opt[i] - costs[i]) * q_opt[i]), 2)
            })
            
        return {
            "solver_converged": bool(res.success),
            "solver_message": str(res.message),
            "target_margin_pct": self.target_portfolio_margin_pct,
            "portfolio_baseline_revenue": round(base_revenue, 2),
            "portfolio_optimized_revenue": round(opt_revenue, 2),
            "portfolio_baseline_profit": round(base_profit, 2),
            "portfolio_optimized_profit": round(opt_profit, 2),
            "profit_uplift_pct": round(((opt_profit - base_profit) / base_profit * 100.0), 2) if base_profit > 0 else 0.0,
            "baseline_margin_pct": round(base_margin, 2),
            "realized_portfolio_margin_pct": round(opt_margin, 2),
            "products": sku_details
        }

if __name__ == "__main__":
    # Test with a bundle of substitute cake stands & tea light holders
    sample_bundle = [
        {"sku": "22423", "name": "REGENCY CAKESTAND 3 TIER", "base_price": 12.75, "unit_cost": 8.29, "base_demand": 150.0, "own_elasticity": -1.30},
        {"sku": "22424", "name": "REGENCY CAKESTAND 2 TIER", "base_price": 8.50, "unit_cost": 5.50, "base_demand": 210.0, "own_elasticity": -1.65},
        {"sku": "22425", "name": "REGENCY TEA PLATE", "base_price": 2.10, "unit_cost": 1.35, "base_demand": 380.0, "own_elasticity": -1.15}
    ]
    
    optimizer = PortfolioCannibalizationOptimizer(target_portfolio_margin_pct=42.0)
    result = optimizer.optimize_portfolio_bundle(sample_bundle)
    
    print("\nPortfolio Cannibalization Optimization Result:")
    import json
    print(json.dumps(result, indent=4))
