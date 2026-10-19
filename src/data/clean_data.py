"""
Data Cleaning and Preprocessing Pipeline
Consolidates Online Retail II sheets, cleans anomalies, standardizes fields,
estimates baseline product unit costs, and saves processed parquet data.
"""

import os
import re
from pathlib import Path
import pandas as pd
import numpy as np

RAW_EXCEL_PATH = Path("data/raw/online_retail_II.xlsx")
PROCESSED_DIR = Path("data/processed")
OUTPUT_PARQUET = PROCESSED_DIR / "b2b_transactions_clean.parquet"
OUTPUT_SAMPLE_CSV = PROCESSED_DIR / "b2b_transactions_sample.csv"

# Non-product stock codes to exclude
EXCLUDED_STOCK_CODES = {
    "POST", "D", "M", "PADS", "DOT", "CRUK", "BANK CHARGES", 
    "AMAZON FEE", "TEST", "TEST001", "TEST002", "ADJUST", "ADJUST2"
}

def load_and_consolidate(file_path: Path) -> pd.DataFrame:
    print(f"Reading '{file_path}' (both sheets: 2009-2010 and 2010-2011)...")
    xls = pd.ExcelFile(file_path)
    dfs = []
    for sheet in xls.sheet_names:
        print(f" - Loading sheet: {sheet}...")
        df_sheet = pd.read_excel(xls, sheet_name=sheet)
        df_sheet["Sheet"] = sheet
        dfs.append(df_sheet)
    df_combined = pd.concat(dfs, ignore_index=True)
    print(f"Consolidated raw rows: {len(df_combined):,}")
    return df_combined

def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    stats = {}
    stats["initial_rows"] = len(df)
    
    # Standardize column names
    df.columns = [col.strip().replace(" ", "_") for col in df.columns]
    
    # 1. Invoice cancellations & formats
    df["Invoice"] = df["Invoice"].astype(str).str.strip()
    cancellation_mask = df["Invoice"].str.startswith("C", na=False) | (df["Quantity"] <= 0)
    stats["cancellations_count"] = int(cancellation_mask.sum())
    
    # Filter out cancellations for demand and pricing modeling
    df_clean = df[~cancellation_mask].copy()
    
    # 2. Filter non-product codes
    df_clean["StockCode"] = df_clean["StockCode"].astype(str).str.strip().str.upper()
    non_product_mask = df_clean["StockCode"].isin(EXCLUDED_STOCK_CODES) | df_clean["StockCode"].str.startswith("POST", na=False)
    stats["non_product_count"] = int(non_product_mask.sum())
    df_clean = df_clean[~non_product_mask]
    
    # 3. Filter invalid / zero prices
    zero_price_mask = df_clean["Price"] <= 0
    stats["zero_price_count"] = int(zero_price_mask.sum())
    df_clean = df_clean[~zero_price_mask]
    
    # 4. Standardize descriptions & Customer ID
    df_clean["Description"] = df_clean["Description"].fillna("UNKNOWN PRODUCT").astype(str).str.strip()
    df_clean["Customer_ID"] = df_clean["Customer_ID"].fillna(-1).astype(int)
    
    # 5. Timestamp and chronological features
    df_clean["InvoiceDate"] = pd.to_datetime(df_clean["InvoiceDate"])
    df_clean = df_clean.sort_values("InvoiceDate").reset_index(drop=True)
    
    df_clean["Year"] = df_clean["InvoiceDate"].dt.year
    df_clean["Month"] = df_clean["InvoiceDate"].dt.month
    df_clean["YearMonth"] = df_clean["InvoiceDate"].dt.to_period("M").astype(str)
    df_clean["DayOfWeek"] = df_clean["InvoiceDate"].dt.dayofweek
    df_clean["DayName"] = df_clean["InvoiceDate"].dt.day_name()
    df_clean["Hour"] = df_clean["InvoiceDate"].dt.hour
    df_clean["Is_Weekend"] = df_clean["DayOfWeek"].isin([5, 6]).astype(int)
    
    # 6. Financial metrics
    df_clean["Revenue"] = (df_clean["Quantity"] * df_clean["Price"]).round(2)
    
    # Wholesale tier identification:
    # In B2B retail/wholesale, pack sizes or batch orders (>= 12 units) represent wholesale purchasing
    df_clean["Is_Wholesale_Order"] = (df_clean["Quantity"] >= 12).astype(int)
    
    # 7. Unit Cost estimation (COGS)
    # Realistic wholesale economics: COGS is estimated at 65% of the product's historical median price
    # (yielding an industry standard target gross margin of 35% at baseline median pricing).
    product_median_price = df_clean.groupby("StockCode")["Price"].median()
    df_clean["Unit_Cost"] = df_clean["StockCode"].map(lambda sc: round(float(product_median_price.get(sc, 1.0)) * 0.65, 2))
    # Ensure unit cost is strictly positive
    df_clean["Unit_Cost"] = df_clean["Unit_Cost"].clip(lower=0.10)
    
    # Gross Profit & Gross Margin
    df_clean["Gross_Profit"] = ((df_clean["Price"] - df_clean["Unit_Cost"]) * df_clean["Quantity"]).round(2)
    df_clean["Gross_Margin_Pct"] = ((df_clean["Gross_Profit"] / df_clean["Revenue"].replace(0, np.nan)) * 100).round(2)
    
    stats["clean_rows"] = len(df_clean)
    stats["unique_products"] = df_clean["StockCode"].nunique()
    stats["unique_customers"] = df_clean[df_clean["Customer_ID"] != -1]["Customer_ID"].nunique()
    stats["total_revenue"] = float(df_clean["Revenue"].sum())
    stats["total_units"] = int(df_clean["Quantity"].sum())
    stats["date_start"] = str(df_clean["InvoiceDate"].min().date())
    stats["date_end"] = str(df_clean["InvoiceDate"].max().date())
    
    return df_clean, stats

def run_pipeline():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    if not RAW_EXCEL_PATH.exists():
        raise FileNotFoundError(f"Missing raw data file: {RAW_EXCEL_PATH}. Please run download_dataset.py first.")
    
    df_raw = load_and_consolidate(RAW_EXCEL_PATH)
    df_clean, stats = clean_data(df_raw)
    
    print("\nData Cleaning Pipeline Summary:")
    print(f" - Initial rows: {stats['initial_rows']:,}")
    print(f" - Cancellations / Returns removed: {stats['cancellations_count']:,}")
    print(f" - Non-product / fees removed: {stats['non_product_count']:,}")
    print(f" - Zero / negative prices removed: {stats['zero_price_count']:,}")
    print(f" - Clean transaction rows: {stats['clean_rows']:,}")
    print(f" - Unique products (SKUs): {stats['unique_products']:,}")
    print(f" - Unique registered B2B customers: {stats['unique_customers']:,}")
    print(f" - Date range: {stats['date_start']} to {stats['date_end']}")
    print(f" - Total Net Revenue: £{stats['total_revenue']:,.2f}")
    print(f" - Total Units Sold: {stats['total_units']:,}")
    
    print(f"\nSaving processed dataset to {OUTPUT_PARQUET}...")
    df_clean.to_parquet(OUTPUT_PARQUET, index=False)
    
    # Also save a sample CSV (first 10,000 rows) for quick viewing/inspection
    df_clean.head(10000).to_csv(OUTPUT_SAMPLE_CSV, index=False)
    print(f"Sample saved to {OUTPUT_SAMPLE_CSV}.")
    print("Data cleaning phase complete!")

if __name__ == "__main__":
    run_pipeline()
