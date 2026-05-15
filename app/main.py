"""
Main entry point for the Pokemon stream API.
"""
from fastapi import FastAPI


app = FastAPI(title="Guardio Pokemon Stream API")

@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
