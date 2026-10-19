"""
FastAPI Application: Dynamic B2B E-Commerce Pricing & Demand Optimization Engine
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import FastAPI, HTTPException, Query, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse

from src.api.schemas import (
    HealthResponse, ProductListResponse,
    ForecastRequest, ForecastResponse,
    PricingRecommendRequest, PricingRecommendResponse,
    PricingResultsResponse, BusinessImpactResponse
)
from src.api.service import service

DASHBOARD_HTML_PATH = Path(__file__).resolve().parent / "templates" / "dashboard.html"

app = FastAPI(
    title="Dynamic B2B E-Commerce Pricing & Demand Optimization Engine",
    description="Production REST API for B2B Demand Forecasting, Dynamic Pricing Recommendations, and Business Impact Tracking.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def get_dashboard():
    """Serves the interactive executive dynamic pricing dashboard."""
    if DASHBOARD_HTML_PATH.exists():
        return HTMLResponse(content=DASHBOARD_HTML_PATH.read_text(encoding="utf-8"))
    return HTMLResponse("<h2>Dynamic Pricing Dashboard Ready</h2><p>Visit <a href='/docs'>/docs</a> for API.</p>")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """Returns empty 204 for browser favicon requests."""
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/health", response_model=HealthResponse, tags=["System Health"])
def get_health():
    """Returns service health status and artifact readiness."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        model_loaded=service.forecaster_bundle is not None,
        products_count=len(service.products_df) if service.products_df is not None else 0
    )

@app.get("/products", response_model=ProductListResponse, tags=["Catalog"])
def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page")
):
    """Retrieves available catalog products with current prices, estimated unit costs, and demand."""
    try:
        return service.get_products(page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/forecast", response_model=ForecastResponse, tags=["Forecasting"])
def generate_demand_forecast(request: ForecastRequest):
    """Generates next-week demand forecast for a given SKU using historical lags and price."""
    try:
        return service.forecast_demand(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.post("/pricing/recommend", response_model=PricingRecommendResponse, tags=["Pricing Optimization"])
def recommend_price(request: PricingRecommendRequest):
    """
    Computes profit-maximizing recommended price for an SKU considering:
    - Product elasticity of demand
    - Hard unit cost + minimum gross margin floor
    - Max allowed price volatility limits
    """
    try:
        return service.recommend_price(request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/pricing/results", response_model=PricingResultsResponse, tags=["Pricing Optimization"])
def get_pricing_results(
    limit: int = Query(100, ge=1, le=5000, description="Max recommendations to return")
):
    """Retrieves saved dynamic pricing recommendations across the catalog."""
    try:
        return service.get_pricing_results(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/business/impact", response_model=BusinessImpactResponse, tags=["Business Impact"])
def get_business_impact():
    """Returns executive metrics comparing static baseline pricing vs. optimized dynamic pricing."""
    try:
        return service.get_business_impact()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)
