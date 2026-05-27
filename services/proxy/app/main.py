"""
Main entry point for the Pokemon stream API.
"""
from fastapi import FastAPI
from app.api.routes import router
from contextlib import asynccontextmanager
from app.services.rules_engine import load_rules

app = FastAPI(title="Pokemon Stream API")
app.include_router(router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the Pokemon stream API.
    """
    app.state.rules = load_rules()
    yield


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
