# Tableau Public Executive Dashboard Design Guide

**Application Target:** Tableau Public 2026.2  
**Local Installation Path:** `C:\Program Files\Tableau\Tableau Public 2026.2\bin\tabpublic.exe`  
**Data Sources Location:** `dashboard/tableau_data/`  

---

## 1. Data Connection Setup

In Tableau Public:
1. Click **Connect to a Data Source** -> **Text File (CSV)**.
2. Select `dashboard/tableau_data/tableau_pricing_recommendations.csv`.
3. Add related connections:
   - `tableau_executive_overview.csv`
   - `tableau_monthly_demand_trends.csv`
   - `tableau_forecast_evaluation.csv`

---

## 2. Tableau Calculated Fields Reference

Copy-paste these exact formulas into Tableau under **Analysis -> Create Calculated Field**:

### A. Gross Profit Uplift (£)
```tableau
[Expected Profit] - [Baseline Profit]
```

### B. Gross Profit Uplift Percentage (%)
```tableau
IF SUM([Baseline Profit]) > 0 THEN
    (SUM([Expected Profit]) - SUM([Baseline Profit])) / SUM([Baseline Profit]) * 100
ELSE
    0
END
```

### C. Revenue Uplift (£)
```tableau
[Expected Revenue] - [Baseline Revenue]
```

### D. Price Action Category (Dimension)
```tableau
IF [Price Change Pct] > 0.5 THEN "Price Increase (+)"
ELSEIF [Price Change Pct] < -0.5 THEN "Price Decrease (-)"
ELSE "Maintain Base Price"
END
```

### E. Safety Margin Status (KPI Flag)
```tableau
IF [Recommended Price] < [Unit Cost] THEN "CRITICAL: Below Cost"
ELSE "Compliant (Margin Protected)"
END
```

---

## 3. Four Core Dashboard Views

### Section 1: Executive KPI Scorecards
- **KPI Card 1: Total Baseline vs. Optimized Profit**
  - Text Shelf: `SUM([Baseline Profit])` and `SUM([Expected Profit])`
  - Sub-label: `[Gross Profit Uplift Percentage]` (+14.4%)
- **KPI Card 2: Projected Net Revenue**
  - Text Shelf: `SUM([Expected Revenue])` (£395.4k)
- **KPI Card 3: Portfolio Size & Strategy Breakdown**
  - Text Shelf: `COUNTD([Sku])` (3,484 active products)
  - Color Badge: Green for +2,160 price increases, Blue for 18 holds, Amber for -1,306 strategic reductions.

### Section 2: Demand Forecasting Analysis
- **Chart:** Dual-Axis Line and Area Chart
  - Columns: `Week Start` (Date - Continuous)
  - Rows: `SUM([Actual Demand])` (Line - Dark Navy) vs. `SUM([LightGBM Pred])` (Dashed Line - Electric Blue)
  - Tooltip: SKU Description, Forecast Error, Absolute % Deviation.

### Section 3: SKU Dynamic Pricing Frontier
- **Chart:** Scatter Plot (Price Change % vs. Gross Profit Uplift £)
  - X-Axis: `[Price Change Pct]` (-20% to +20%)
  - Y-Axis: `[Margin Uplift GBP]`
  - Size: `[Baseline Demand]`
  - Color: `[Action Type]` (Green = Increase, Coral = Decrease, Grey = Hold)
  - Detail: `[Sku]`, `[Description]`, `[Rationale]`

### Section 4: Country & Regional Wholesale Demand
- **Chart:** Filled Symbol Map / Horizontal Bar
  - Dimension: `Country`
  - Measure: `SUM([Total Revenue])`, `SUM([Wholesale Units])`
  - Tooltip: Geographic distribution of B2B export revenue.

---

## 4. Interactive Filters to Place on Dashboard
- **Filter 1:** `Action Type` (Single / Multi-select drop-down)
- **Filter 2:** `Elasticity Segment` (Inelastic vs. Highly Elastic)
- **Filter 3:** `Price Change Range` (Continuous slider: -20% to +20%)
- **Filter 4:** `Country` (Top 10 B2B wholesale markets)
