# Dynamic B2B E-Commerce Pricing & Demand Optimization Engine

An end-to-end, production-grade Machine Learning and Business Intelligence solution designed to forecast wholesale demand, recommend profit-maximizing dynamic prices, enforce strict margin and volatility guardrails, and quantify business impact against static baseline pricing.

---

## 📌 Executive Summary & Key Results

Using 2 years of authentic transaction records from **Online Retail II (1,037,361 cleaned transactions across 3,484 active B2B wholesale SKUs)**, this engine delivered:

| Metric | Static Baseline Strategy | Dynamic Optimized Pricing | Business Delta |
| :--- | :--- | :--- | :--- |
| **Gross Profit** | **£186,195.54** | **£213,047.98** | **+£26,852.44 (+14.42% Uplift)** |
| **Gross Margin %** | 49.60% | 53.87% | **+4.27% pts Margin Expansion** |
| **Total Revenue** | £375,340.23 | £395,463.52 | **+£20,123.29 (+5.36% Uplift)** |
| **Safety Violations (Price < Cost)** | — | **0 Violations** | **100% Hard Cost-Floor Compliant** |

---

## 🏛️ System Architecture

```
[ Online Retail II Real B2B Dataset (1.06M rows) ]
                       │
                       ▼
       [ Phase 1: Ingestion & EDA Engine ]
       - Cleans returns ('C' prefixes) & non-products
       - Derives wholesale tiers & empirical COGS
                       │
                       ▼
       [ Phase 2: Demand Forecasting Engine ]
       - LightGBM, XGBoost, and Rolling Baselines
       - Chronological 82/18 Train/Test Splits
                       │
                       ▼
    [ Phase 3: Dynamic Price Optimization Engine ]
    - SKU Empirical Price Elasticity Estimation
    - Unit Cost + 15% Margin Floor | Max 20% Volatility Cap
                       │
                       ▼
     [ Phase 4: Static vs. Dynamic Impact Engine ]
     - Quantifies Revenue & Margin Uplift
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
[ Phase 5: FastAPI REST API ]  [ Phase 6: Tableau BI Dashboard ]
- /health, /products           - 4 Denormalized CSV Data Feeds
- /forecast, /pricing/recommend - Executive Scorecards & Frontier
```

---

## 📂 Project Repository Structure

```
Dynamic B2B E-Commerce Pricing & Demand Optimization Engine/
├── data/
│   ├── raw/                      # Downloaded Online Retail II excel & archives
│   ├── processed/                # Cleaned parquet data & weekly demand panels
│   └── outputs/                  # Reports, metrics JSONs, and figure charts
│       ├── figures/              # Analytical plots (elasticity, forecast, Pareto)
│       ├── business_impact_report.md
│       ├── data_quality_report.md
│       ├── forecast_evaluation_report.md
│       └── pricing_recommendations.parquet
├── models/                       # Serialized LightGBM/XGBoost model bundles
├── src/
│   ├── data/
│   │   ├── download_dataset.py   # Automated dataset retriever
│   │   ├── clean_data.py         # Data cleaning & COGS estimation
│   │   └── eda_analysis.py       # Exploratory analysis & report generator
│   ├── forecasting/
│   │   ├── feature_engineering.py# Lags, rolling stats, chronological splits
│   │   └── train_forecasting.py  # Model training & WAPE evaluation
│   ├── optimization/
│   │   └── price_optimizer.py    # Elasticity & constrained profit maximization
│   ├── evaluation/
│   │   └── business_impact.py    # Static vs. dynamic financial evaluation
│   └── api/
│       ├── main.py               # FastAPI application
│       ├── schemas.py            # Pydantic input/output schemas
│       └── service.py            # Model inference & lookup layer
├── dashboard/
│   ├── prepare_tableau_data.py   # Exports Tableau CSV feeds
│   ├── TABLEAU_DASHBOARD_GUIDE.md# Visual workbook construction manual
│   └── tableau_data/             # Generated CSV feeds for Tableau Public
├── deployment/
│   ├── Dockerfile                # Production multi-stage containerfile
│   ├── docker-compose.yml        # Local orchestration
│   └── CLOUD_ARCHITECTURE.md     # Enterprise AWS & Azure blueprint
├── tests/
│   ├── test_api.py               # Integration tests for FastAPI endpoints
│   └── test_reliability_and_edge_cases.py # Robustness & constraint tests
├── requirements.txt              # Production Python dependencies
├── .env.example                  # Environment configuration template
└── README.md                     # Comprehensive project manual
```

---

## 🚀 Quickstart & Reproduction Guide

### 1. Environment Setup
```powershell
# Clone or navigate to the project directory
cd "C:\Projects\Dynamic B2B E-Commerce Pricing & Demand Optimization Engine"

# Create and activate virtual environment
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install verified dependencies
pip install -r requirements.txt
```

### 2. Run the Full End-to-End Pipeline
```powershell
# Phase 1: Ingestion, Cleaning & EDA
python src/data/download_dataset.py
python src/data/clean_data.py
python src/data/eda_analysis.py

# Phase 2: Feature Engineering & Model Training
python src/forecasting/train_forecasting.py

# Phase 3 & 4: Dynamic Pricing Optimization & Business Impact
python src/evaluation/business_impact.py

# Phase 6: Prepare Tableau BI Data Feeds
python dashboard/prepare_tableau_data.py
```

### 3. Launch the FastAPI Backend Service
```powershell
# Start the API server on localhost:8000
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger API documentation is available at: **`http://127.0.0.1:8000/docs`**

### 4. Execute Automated Test Suite
```powershell
# Run all 15 automated integration and edge-case unit tests
pytest tests/ -v
```

---

## 📊 Tableau Public Integration

The project is integrated with **Tableau Public 2026.2** (installed on Windows at `C:\Program Files\Tableau\Tableau Public 2026.2`).
Pre-built, clean CSV feeds are available in [`dashboard/tableau_data/`](file:///c:/Projects/Dynamic%20B2B%20E-Commerce%20Pricing%20&%20Demand%20Optimization%20Engine/dashboard/tableau_data):
1. `tableau_executive_overview.csv`: Executive KPI scorecards and financial comparisons.
2. `tableau_pricing_recommendations.csv`: SKU-level recommended prices, expected profit uplift, and human-readable rationales.
3. `tableau_monthly_demand_trends.csv`: Time-series trends and geographic wholesale distributions.
4. `tableau_forecast_evaluation.csv`: Holdout actual vs. predicted demand by product.

Refer to [`dashboard/TABLEAU_DASHBOARD_GUIDE.md`](file:///c:/Projects/Dynamic%20B2B%20E-Commerce%20Pricing%20&%20Demand%20Optimization%20Engine/dashboard/TABLEAU_DASHBOARD_GUIDE.md) for step-by-step workbook creation.

---

## ☁️ Cloud Deployment (AWS ECS & Azure Container Apps)

Refer to [`deployment/CLOUD_ARCHITECTURE.md`](file:///c:/Projects/Dynamic%20B2B%20E-Commerce%20Pricing%20&%20Demand%20Optimization%20Engine/deployment/CLOUD_ARCHITECTURE.md) for:
- Infrastructure-as-Code blueprints using AWS ECS Fargate, ALB, S3, and CloudWatch.
- Horizontal auto-scaling policies based on traffic volume.
- Zero-cost local container execution via `docker compose -f deployment/docker-compose.yml up`.
