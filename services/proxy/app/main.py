"""
Main entry point for the Pokemon stream API.
"""
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Pokemon Stream API")
app.include_router(router)


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
