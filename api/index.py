"""
Vercel Serverless Function Entrypoint for Dynamic B2B E-Commerce Pricing & Demand Optimization Engine.
Exposes the FastAPI application to Vercel's Python runtime.
"""
import sys
from pathlib import Path

# Add project root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.api.main import app

# Export ASGI app for Vercel
__all__ = ["app"]
