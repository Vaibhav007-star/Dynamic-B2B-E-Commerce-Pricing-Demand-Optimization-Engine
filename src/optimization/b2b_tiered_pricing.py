"""
Advancement 1: B2B Multi-Tier Volume Pricing & Customer Segmentation Engine
Implements wholesale RFM customer clustering and dynamic volume-break discount schedules
with guaranteed margin floor protection.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

TRANSACTIONS_PATH = Path("data/processed/b2b_transactions_clean.parquet")
OUTPUTS_DIR = Path("data/outputs")

class B2BTieredPricingEngine:
    def __init__(self, n_clusters: int = 3, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        self.customer_segments = {}
        self.segment_profiles = {}
        
    def fit_customer_segments(self, df: pd.DataFrame = None):
        """
        Segments registered B2B accounts using RFM + Wholesale Purchase Concentration.
        """
        if df is None:
            if not TRANSACTIONS_PATH.exists():
                raise FileNotFoundError(f"Missing {TRANSACTIONS_PATH}")
            df = pd.read_parquet(TRANSACTIONS_PATH)
            
        # Filter to registered commercial accounts
        cust_df = df[df["Customer_ID"] != -1].copy()
        
        ref_date = cust_df["InvoiceDate"].max()
        rfm = cust_df.groupby("Customer_ID").agg(
            Recency=("InvoiceDate", lambda d: (ref_date - d.max()).days),
            Frequency=("Invoice", "nunique"),
            Monetary=("Revenue", "sum"),
            Wholesale_Ratio=("Is_Wholesale_Order", "mean"),
            Avg_Units_Per_Order=("Quantity", "mean")
        ).reset_index()
        
        # Log-transform skewed monetary & frequency fields
        features = ["Recency", "Frequency", "Monetary", "Wholesale_Ratio"]
        X = rfm[features].copy()
        X["Frequency"] = np.log1p(X["Frequency"])
        X["Monetary"] = np.log1p(X["Monetary"].clip(lower=0))
        
        X_scaled = self.scaler.fit_transform(X)
        rfm["Cluster"] = self.kmeans.fit_predict(X_scaled)
        
        # Order clusters by Monetary spend: 0 = Spot Buyer, 1 = Trade Account, 2 = Enterprise Wholesaler
        cluster_order = rfm.groupby("Cluster")["Monetary"].mean().sort_values().index.tolist()
        label_map = {
            cluster_order[0]: "Spot Retail Buyer",
            cluster_order[1]: "Trade / Boutique Account",
            cluster_order[2]: "Enterprise Wholesaler"
        }
        discount_multiplier_map = {
            cluster_order[0]: 1.00,  # Standard pricing
            cluster_order[1]: 0.95,  # 5% relationship discount
            cluster_order[2]: 0.90   # 10% enterprise volume discount
        }
        
        rfm["Segment_Name"] = rfm["Cluster"].map(label_map)
        rfm["Segment_Discount_Factor"] = rfm["Cluster"].map(discount_multiplier_map)
        
        # Store lookup
        self.customer_segments = rfm.set_index("Customer_ID")[["Segment_Name", "Segment_Discount_Factor", "Monetary", "Frequency"]].to_dict(orient="index")
        
        # Segment profiles summary
        profiles = rfm.groupby("Segment_Name").agg(
            Account_Count=("Customer_ID", "count"),
            Avg_Spend_GBP=("Monetary", "mean"),
            Avg_Orders=("Frequency", "mean"),
            Avg_Recency_Days=("Recency", "mean"),
            Avg_Wholesale_Pct=("Wholesale_Ratio", lambda s: float(s.mean() * 100))
        ).reset_index()
        
        self.segment_profiles = profiles.to_dict(orient="records")
        print(f"Segmented {len(rfm):,} B2B accounts into 3 cohorts:")
        for p in self.segment_profiles:
            print(f" - {p['Segment_Name']}: {p['Account_Count']:,} accounts, Avg Spend £{p['Avg_Spend_GBP']:,.2f}")
            
        return rfm

    def calculate_volume_tier_schedule(
        self,
        base_recommended_price: float,
        unit_cost: float,
        elasticity: float = -1.45,
        min_gross_margin_pct: float = 15.0
    ) -> dict:
        """
        Generates volume break price tiers:
        - Tier 1: 1 - 11 units (Spot order)
        - Tier 2: 12 - 49 units (Wholesale Case Pack, typically 6% discount)
        - Tier 3: 50+ units (Bulk Pallet Tier, typically 12% discount)
        Strictly guarantees: Tier_Price >= unit_cost * (1 + min_margin).
        """
        hard_floor = unit_cost * (1.0 + min_gross_margin_pct / 100.0)
        
        # Base spot price (Tier 1)
        p_tier1 = max(base_recommended_price, hard_floor)
        
        # Volume break discount targets
        discount_tier2_pct = 6.0
        discount_tier3_pct = 12.0
        
        # Dynamic elasticity adjustment: if highly elastic (|e| > 2), give deeper volume discounts
        if elasticity < -1.8:
            discount_tier2_pct = 8.0
            discount_tier3_pct = 15.0
        elif elasticity > -1.0: # Inelastic
            discount_tier2_pct = 4.0
            discount_tier3_pct = 8.0
            
        p_tier2 = max(p_tier1 * (1.0 - discount_tier2_pct / 100.0), hard_floor)
        p_tier3 = max(p_tier1 * (1.0 - discount_tier3_pct / 100.0), hard_floor)
        
        # Guaranteed strict monotonic order: p_tier1 >= p_tier2 >= p_tier3 >= hard_floor
        if p_tier2 > p_tier1:
            p_tier2 = p_tier1
        if p_tier3 > p_tier2:
            p_tier3 = p_tier2
            
        return {
            "tier_1_spot": {
                "quantity_range": "1 - 11 units",
                "unit_price": round(p_tier1, 2),
                "discount_pct": 0.0,
                "gross_margin_pct": round(((p_tier1 - unit_cost) / p_tier1) * 100.0, 2)
            },
            "tier_2_case": {
                "quantity_range": "12 - 49 units (Case Pack)",
                "unit_price": round(p_tier2, 2),
                "discount_pct": round(((p_tier1 - p_tier2) / p_tier1) * 100.0, 2),
                "gross_margin_pct": round(((p_tier2 - unit_cost) / p_tier2) * 100.0, 2)
            },
            "tier_3_bulk": {
                "quantity_range": "50+ units (Bulk Pallet)",
                "unit_price": round(p_tier3, 2),
                "discount_pct": round(((p_tier1 - p_tier3) / p_tier1) * 100.0, 2),
                "gross_margin_pct": round(((p_tier3 - unit_cost) / p_tier3) * 100.0, 2)
            },
            "governance": {
                "unit_cost": round(unit_cost, 2),
                "margin_floor_pct": min_gross_margin_pct,
                "floor_price": round(hard_floor, 2),
                "cost_floor_protected": p_tier3 >= hard_floor
            }
        }

    def get_customer_quote(self, customer_id: int, sku: str, base_recommended_price: float, unit_cost: float, quantity: int) -> dict:
        """
        Produces a personalized contract quote combining customer relationship tier and volume order size.
        """
        schedule = self.calculate_volume_tier_schedule(base_recommended_price, unit_cost)
        
        # Determine quantity tier
        if quantity < 12:
            tier_key = "tier_1_spot"
        elif quantity < 50:
            tier_key = "tier_2_case"
        else:
            tier_key = "tier_3_bulk"
            
        tier_price = schedule[tier_key]["unit_price"]
        
        # Apply customer relationship discount factor
        cust_info = self.customer_segments.get(customer_id, {
            "Segment_Name": "Spot Retail Buyer",
            "Segment_Discount_Factor": 1.00
        })
        
        seg_discount_factor = cust_info["Segment_Discount_Factor"]
        hard_floor = schedule["governance"]["floor_price"]
        
        # Final agreed unit price
        final_unit_price = max(round(tier_price * seg_discount_factor, 2), hard_floor)
        total_order_value = round(final_unit_price * quantity, 2)
        total_gross_profit = round((final_unit_price - unit_cost) * quantity, 2)
        margin_pct = round((total_gross_profit / total_order_value) * 100.0, 2) if total_order_value > 0 else 0.0
        
        return {
            "customer_id": customer_id,
            "segment_name": cust_info["Segment_Name"],
            "sku": sku,
            "order_quantity": quantity,
            "applied_tier": schedule[tier_key]["quantity_range"],
            "tier_base_price": tier_price,
            "relationship_factor": seg_discount_factor,
            "final_quoted_unit_price": final_unit_price,
            "total_order_value": total_order_value,
            "total_gross_profit": total_gross_profit,
            "realized_margin_pct": margin_pct,
            "margin_floor_protected": final_unit_price >= hard_floor
        }

if __name__ == "__main__":
    engine = B2BTieredPricingEngine()
    engine.fit_customer_segments()
    
    # Test volume tier schedule for high-volume SKU
    sample_schedule = engine.calculate_volume_tier_schedule(
        base_recommended_price=3.54,
        unit_cost=1.92,
        elasticity=-1.45
    )
    print("\nSample Volume-Break Schedule for SKU 85123A:")
    print(json.dumps(sample_schedule, indent=4))
