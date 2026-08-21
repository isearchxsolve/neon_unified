"""FastAPI entrypoint for the oiioii clone final app.

Run: uvicorn backend.main:app --reload
"""
from src.api import create_app

app = create_app()
