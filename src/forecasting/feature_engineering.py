"""
Feature Engineering for SKU-level Demand Forecasting
Aggregates clean transaction data into weekly product-level demand panels,
computes lag and rolling window features, and applies chronological train/test splitting.
"""

from pathlib import Path
import pandas as pd
import numpy as np

PROCESSED_DATA_PATH = Path("data/processed/b2b_transactions_clean.parquet")
OUTPUT_PANEL_PATH = Path("data/processed/demand_weekly_panel.parquet")

def build_weekly_demand_panel(df: pd.DataFrame, min_weeks_active: int = 15) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    print("Aggregating transactions to Weekly SKU-level demand...")
    
    # Floor invoice date to Monday of each week
    df["Week_Start"] = df["InvoiceDate"].dt.to_period("W").apply(lambda r: r.start_time)
    
    # Weekly aggregation per product
    sku_weekly = df.groupby(["StockCode", "Week_Start"]).agg(
        Weekly_Demand=("Quantity", "sum"),
        Avg_Price=("Price", "mean"),
        Min_Price=("Price", "min"),
        Max_Price=("Price", "max"),
        Order_Count=("Invoice", "nunique"),
        Wholesale_Order_Count=("Is_Wholesale_Order", "sum"),
        Total_Revenue=("Revenue", "sum"),
        Description=("Description", "first")
    ).reset_index()
    
    # Filter products with sufficient historical transaction presence
    product_week_counts = sku_weekly.groupby("StockCode")["Week_Start"].nunique()
    active_skus = product_week_counts[product_week_counts >= min_weeks_active].index
    print(f"Total SKUs: {len(product_week_counts):,}. SKUs with >= {min_weeks_active} active weeks: {len(active_skus):,}")
    
    sku_weekly = sku_weekly[sku_weekly["StockCode"].isin(active_skus)].copy()
    
    # Complete the weekly panel grid for each SKU (filling missing weeks with 0 demand)
    all_weeks = pd.date_range(start=sku_weekly["Week_Start"].min(), end=sku_weekly["Week_Start"].max(), freq="W-MON")
    grid_dfs = []
    
    sku_meta = sku_weekly.groupby("StockCode").agg(
        Median_Price=("Avg_Price", "median"),
        Description=("Description", "first")
    ).reset_index()
    
    for sku in active_skus:
        sku_df = sku_weekly[sku_weekly["StockCode"] == sku].set_index("Week_Start").reindex(all_weeks)
        sku_df["StockCode"] = sku
        sku_df["Weekly_Demand"] = sku_df["Weekly_Demand"].fillna(0)
        # Forward fill price or fallback to SKU median
        sku_med = sku_meta.loc[sku_meta["StockCode"] == sku, "Median_Price"].values[0]
        sku_desc = sku_meta.loc[sku_meta["StockCode"] == sku, "Description"].values[0]
        sku_df["Avg_Price"] = sku_df["Avg_Price"].ffill().bfill().fillna(sku_med)
        sku_df["Description"] = sku_desc
        sku_df["Order_Count"] = sku_df["Order_Count"].fillna(0)
        sku_df["Wholesale_Order_Count"] = sku_df["Wholesale_Order_Count"].fillna(0)
        sku_df["Week_Start"] = sku_df.index
        grid_dfs.append(sku_df)
        
    panel = pd.concat(grid_dfs, ignore_index=True)
    panel = panel.sort_values(["StockCode", "Week_Start"]).reset_index(drop=True)
    
    print("Generating temporal, lag, and rolling features...")
    # Calendar features
    panel["Month"] = panel["Week_Start"].dt.month
    panel["Quarter"] = panel["Week_Start"].dt.quarter
    panel["Week_Of_Year"] = panel["Week_Start"].dt.isocalendar().week.astype(int)
    panel["Is_Q4"] = panel["Quarter"].apply(lambda q: 1 if q == 4 else 0)
    
    # Lagged demand features
    for lag in [1, 2, 4, 8]:
        panel[f"Lag_{lag}_Demand"] = panel.groupby("StockCode")["Weekly_Demand"].shift(lag)
    
    # Rolling averages (using lag 1 to prevent data leakage)
    panel["Rolling_Mean_4w"] = panel.groupby("StockCode")["Weekly_Demand"].transform(
        lambda s: s.shift(1).rolling(4, min_periods=1).mean()
    )
    panel["Rolling_Mean_8w"] = panel.groupby("StockCode")["Weekly_Demand"].transform(
        lambda s: s.shift(1).rolling(8, min_periods=1).mean()
    )
    panel["Rolling_Std_4w"] = panel.groupby("StockCode")["Weekly_Demand"].transform(
        lambda s: s.shift(1).rolling(4, min_periods=1).std()
    ).fillna(0)
    
    # Price dynamic features
    panel["Lag_1_Price"] = panel.groupby("StockCode")["Avg_Price"].shift(1).fillna(panel["Avg_Price"])
    panel["Price_Ratio_to_Lag"] = (panel["Avg_Price"] / panel["Lag_1_Price"].replace(0, np.nan)).fillna(1.0)
    
    # Drop rows with NaN from lag_8
    panel_clean = panel.dropna(subset=["Lag_8_Demand"]).reset_index(drop=True)
    
    # Chronological Train / Test Split (Last 15% of calendar weeks used as holdout test set)
    unique_weeks = sorted(panel_clean["Week_Start"].unique())
    split_idx = int(len(unique_weeks) * 0.82)
    split_date = unique_weeks[split_idx]
    
    train_df = panel_clean[panel_clean["Week_Start"] < split_date].copy()
    test_df = panel_clean[panel_clean["Week_Start"] >= split_date].copy()
    
    print(f"Panel rows: {len(panel_clean):,} across {len(active_skus):,} SKUs")
    print(f"Chronological Split Date: {split_date.strftime('%Y-%m-%d')}")
    print(f" - Train set: {len(train_df):,} rows ({train_df['Week_Start'].min().date()} to {train_df['Week_Start'].max().date()})")
    print(f" - Test set:  {len(test_df):,} rows ({test_df['Week_Start'].min().date()} to {test_df['Week_Start'].max().date()})")
    
    OUTPUT_PANEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    panel_clean.to_parquet(OUTPUT_PANEL_PATH, index=False)
    print(f"Weekly demand panel saved to {OUTPUT_PANEL_PATH}")
    
    return panel_clean, train_df, test_df

if __name__ == "__main__":
    df = pd.read_parquet(PROCESSED_DATA_PATH)
    build_weekly_demand_panel(df)
