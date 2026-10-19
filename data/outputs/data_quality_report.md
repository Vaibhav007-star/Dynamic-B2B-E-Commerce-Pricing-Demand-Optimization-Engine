# Data Quality Report: Dynamic B2B E-Commerce Pricing & Demand Optimization

**Dataset:** Online Retail II (Consolidated 2-Year Real B2B/Wholesale Transactions)  
**Date Range:** 2009-12-01 to 2011-12-09  
**Total Cleaned Transactions:** 1,037,361  
**Total Units Sold:** 11,403,015  
**Total Net Revenue:** £20,170,821.21  
**Total Gross Profit:** £6,156,774.48 (30.52% Margin)  

---

## 1. Executive Summary & Problem Context

The dataset represents authentic transaction histories of a UK-based non-store online retailer and wholesaler operating internationally across Europe, North America, and Asia.
A substantial proportion of buyers purchase in commercial batch sizes (>= 12 units), characteristic of retail resale, boutique distributors, and corporate wholesale.

### Key Observations:
1. **Wholesale Concentration:** Bulk wholesale orders (>=12 units) account for **78.6%** of all physical units moved, demonstrating clear B2B transaction dynamics.
2. **Seasonal Peaks:** Demand accelerates strongly between September and November (Q4 pre-holiday stocking by retail re-sellers), followed by post-holiday normalization in January/February.
3. **Price Variation:** Over the 2-year period, prices vary naturally due to volume discounts, seasonal promotions, and currency fluctuations, providing empirical variation required for price elasticity and dynamic pricing modeling.

---

## 2. Data Cleaning & Integrity Audit

| Metric | Raw Value | Post-Clean Value | Filtering Rationale |
| :--- | :--- | :--- | :--- |
| **Total Rows** | 1,067,371 | 1,037,361 | Removed returns, non-product line items, zero-price entries |
| **Cancellations / Returns** | ~19,494 | 0 in active demand | Invoices prefixed with 'C' & negative quantities separated |
| **Non-Product Codes** | ~4,200 | 0 | Filtered postage (`POST`), manual adjustments (`M`, `D`), bank charges |
| **Unique Products (SKUs)** | 5,305 | 4,735 | High SKU catalog coverage |
| **B2B Registered Accounts** | 5,881 | 5,853 | Unique commercial accounts |
| **Zero/Negative Prices** | ~2,500 | 0 | Invalid ledger entries and bad debts eliminated |

---

## 3. Financial Assumptions & Unit Cost (COGS) Estimation

In authentic wholesale datasets, supplier COGS (Cost of Goods Sold) is proprietary and withheld. To perform rigorous dynamic pricing optimization and calculate gross margin uplift:
- **Baseline Unit Cost:** Derived per SKU as **65% of the SKU's historical median selling price**, clipped to a minimum of £0.10.
- **Economic Realism:** This establishes an authentic **35% baseline gross margin floor**, matching wholesale distributor benchmark margins.
- **Safety Rule:** No dynamic pricing algorithm is permitted to recommend prices below this computed unit cost.

---

## 4. Visual Deliverables Generated

The following analytical figures have been generated and saved to `data/outputs/figures/`:
1. `monthly_revenue_and_volume.png`: Long-term revenue and demand seasonality across the 24-month horizon.
2. `top_products_revenue.png`: Pareto distribution of top-grossing wholesale SKUs.
3. `wholesale_share.png`: Comparison of wholesale batch volume vs individual orders.
4. `price_demand_elasticity_sample.png`: Empirical price vs demand curve exhibiting classical downward-sloping elasticity.

---

## 5. Next Steps for Phase 2 (Demand Forecasting)
- Aggregate daily and weekly SKU-level demand.
- Build chronological train/test splits (e.g. 80% train, 20% test) to prevent future data leakage.
- Extract calendar, lag, and rolling statistics.
- Train LightGBM and XGBoost demand forecasting models.
