# Business Impact Evaluation: Static Baseline vs. Dynamic Pricing

**Total Portfolio SKUs Evaluated:** 3,484  
**Evaluation Methodology:** Out-of-time holdout simulation with empirical price-elasticity response curves  
**Constraint Governance:** Hard safety floor at unit cost + 15% minimum margin, max 20% price volatility cap  

---

## 1. Executive Financial Summary

| Key Financial Metric | Static Baseline Strategy | Optimized Dynamic Pricing | Absolute Impact | Relative Delta (%) |
| :--- | :--- | :--- | :--- | :--- |
| **Gross Profit** | **£186,195.54** | **£213,047.98** | **+£26,852.44** | **+14.42%** |
| **Gross Margin %** | 49.60% | 53.87% | +4.27% pts | — |
| **Total Revenue** | £375,395.56 | £395,518.85 | +20,123.29 | +5.36% |
| **Units Demanded** | 156,576.4 | 148,695.7 | -7,880.7 | -5.03% |

---

## 2. Portfolio Strategy Breakdown

- **Price Increases Recommended:** **2160 SKUs (62.0%)**  
  *Context:* Commodities with low price sensitivity (inelastic demand) where margin gains significantly outpace minor unit volume attrition.
- **Price Decreases Recommended:** **1306 SKUs (37.5%)**  
  *Context:* Highly price-sensitive SKUs (elastic demand) where competitive price reductions stimulate high sales volumes, unlocking incremental gross profit dollars.
- **Prices Maintained (Holds):** **18 SKUs (0.5%)**  
  *Context:* Products already at the profit-maximizing frontier or restrained by margin constraints.

---

## 3. Top Gross-Profit Generating SKUs

| SKU | Description | Base Price | Recommended Price | Demand Shift | Gross Profit Shift |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `23084` | RABBIT NIGHT LIGHT | £2.30 | £2.77 (+20.0%) | 3432 -> 2635 | £3275.36 -> £3728.74 |
| `79321` | CHILLI LIGHTS | £8.85 | £10.63 (+20.0%) | 536 -> 430 | £3020.24 -> £3185.38 |
| `22086` | PAPER CHAIN KIT 50'S CHRIS | £3.27 | £3.92 (+20.0%) | 1713 -> 1315 | £2309.13 -> £2632.30 |
| `85099B` | JUMBO BAG RED WHITE SPOTTY | £2.61 | £3.13 (+20.0%) | 1401 -> 1223 | £1880.26 -> £2280.03 |
| `22197` | POPCORN HOLDER , SMALL | £1.05 | £1.26 (+20.0%) | 3319 -> 3079 | £1664.91 -> £2191.96 |
| `22423` | REGENCY CAKESTAND 3 TIER | £16.15 | £19.38 (+20.0%) | 225 -> 173 | £1770.85 -> £1918.07 |
| `22114` | HOT WATER BOTTLE TEA AND S | £5.62 | £4.50 (-20.0%) | 452 -> 817 | £1377.08 -> £1572.92 |
| `22910` | PAPER CHAIN KIT VINTAGE CH | £3.48 | £4.18 (+20.0%) | 884 -> 679 | £1381.52 -> £1533.37 |
| `85123A` | WHITE HANGING HEART T-LIGH | £3.59 | £3.16 (-12.0%) | 889 -> 1232 | £1484.94 -> £1527.24 |
| `84029E` | RED WOOLLY HOTTIE WHITE HE | £5.82 | £4.66 (-20.0%) | 326 -> 675 | £1101.50 -> £1496.54 |

---

## 4. Safety & Governance Audit

- **Prices Below Cost:** **0 violations** (100% compliant with minimum margin floor).
- **Price Volatility:** **100% within the [-20%, +20%] boundary** to maintain buyer trust and prevent wholesale customer churn.
- **Data Availability:** Pricing recommendations exported to `data/outputs/pricing_recommendations.parquet` for FastAPI consumption and Tableau BI integration.
