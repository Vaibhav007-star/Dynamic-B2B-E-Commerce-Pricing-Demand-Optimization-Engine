"""
Prepares clean, denormalized, Tableau-ready CSV and Hyper-friendly data feeds.
Outputs to dashboard/tableau_data/
"""

from pathlib import Path
import json
import pandas as pd
import numpy as np

OUTPUTS_DIR = Path("data/outputs")
PROCESSED_DIR = Path("data/processed")
TABLEAU_DIR = Path("dashboard/tableau_data")

def prepare_tableau_feeds():
    TABLEAU_DIR.mkdir(parents=True, exist_ok=True)
    print("Exporting Tableau-ready datasets...")

    # 1. Executive Summary Table
    impact_json_path = OUTPUTS_DIR / "business_impact_summary.json"
    with open(impact_json_path, "r") as f:
        impact = json.load(f)
        
    exec_df = pd.DataFrame([{
        "Metric_Group": "Executive Financials",
        "Total_SKUs_Analyzed": impact["products_analyzed"],
        "Baseline_Revenue_GBP": impact["total_baseline_revenue"],
        "Optimized_Revenue_GBP": impact["total_optimized_revenue"],
        "Revenue_Uplift_GBP": impact["revenue_change"],
        "Revenue_Uplift_Pct": impact["relative_revenue_change_pct"],
        "Baseline_Gross_Profit_GBP": impact["total_baseline_gross_profit"],
        "Optimized_Gross_Profit_GBP": impact["total_optimized_gross_profit"],
        "Gross_Profit_Uplift_GBP": impact["gross_profit_change"],
        "Gross_Profit_Uplift_Pct": impact["relative_gross_profit_improvement_pct"],
        "Baseline_Gross_Margin_Pct": impact["baseline_gross_margin_pct"],
        "Optimized_Gross_Margin_Pct": impact["optimized_gross_margin_pct"],
        "Price_Increases_Count": impact["price_actions"]["price_increases"],
        "Price_Decreases_Count": impact["price_actions"]["price_decreases"],
        "Price_Holds_Count": impact["price_actions"]["price_holds"],
        "Cost_Floor_Violations": impact["safety_checks"]["prices_below_cost"]
    }])
    exec_df.to_csv(TABLEAU_DIR / "tableau_executive_overview.csv", index=False)
    print(" - Saved tableau_executive_overview.csv")

    # 2. SKU Pricing Recommendations
    rec_path = OUTPUTS_DIR / "pricing_recommendations.parquet"
    rec_df = pd.read_parquet(rec_path)
    
    # Add category heuristics and action tags for easy Tableau filtering
    rec_df["Action_Type"] = np.where(
        rec_df["price_change_pct"] > 0.5, "Price Increase",
        np.where(rec_df["price_change_pct"] < -0.5, "Price Decrease", "Maintain Price")
    )
    rec_df["Elasticity_Segment"] = np.where(
        rec_df["elasticity"] > -1.0, "Inelastic (|e| < 1.0)",
        np.where(rec_df["elasticity"] < -2.0, "Highly Elastic (|e| > 2.0)", "Moderately Elastic (1.0 <= |e| <= 2.0)")
    )
    rec_df["Margin_Uplift_GBP"] = rec_df["expected_profit"] - rec_df["baseline_profit"]
    
    rec_df.to_csv(TABLEAU_DIR / "tableau_pricing_recommendations.csv", index=False)
    print(f" - Saved tableau_pricing_recommendations.csv ({len(rec_df):,} rows)")

    # 3. Monthly Demand & Revenue Time-Series
    clean_tx_path = PROCESSED_DIR / "b2b_transactions_clean.parquet"
    tx_df = pd.read_parquet(clean_tx_path, columns=["YearMonth", "Revenue", "Gross_Profit", "Quantity", "Is_Wholesale_Order", "Country"])
    
    monthly_geo = tx_df.groupby(["YearMonth", "Country"]).agg(
        Total_Revenue=("Revenue", "sum"),
        Total_Gross_Profit=("Gross_Profit", "sum"),
        Total_Units=("Quantity", "sum"),
        Wholesale_Units=("Quantity", lambda q: tx_df.loc[q.index, "Quantity"][tx_df.loc[q.index, "Is_Wholesale_Order"] == 1].sum())
    ).reset_index()
    monthly_geo["YearMonth_Date"] = pd.to_datetime(monthly_geo["YearMonth"] + "-01")
    monthly_geo.to_csv(TABLEAU_DIR / "tableau_monthly_demand_trends.csv", index=False)
    print(" - Saved tableau_monthly_demand_trends.csv")

    # 4. Holdout Forecast Predictions
    preds_path = OUTPUTS_DIR / "demand_forecast_predictions.parquet"
    preds_df = pd.read_parquet(preds_path)
    preds_df["Forecast_Error_Units"] = preds_df["LightGBM_Pred"] - preds_df["Actual_Demand"]
    preds_df["Abs_Forecast_Error"] = preds_df["Forecast_Error_Units"].abs()
    preds_df.to_csv(TABLEAU_DIR / "tableau_forecast_evaluation.csv", index=False)
    print(f" - Saved tableau_forecast_evaluation.csv ({len(preds_df):,} rows)")

    print("All Tableau data sources ready in dashboard/tableau_data/")

if __name__ == "__main__":
    prepare_tableau_feeds()
