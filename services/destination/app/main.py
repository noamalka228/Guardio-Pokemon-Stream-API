"""
Destination Service for receiving matched Pokemon requests.
"""
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Pokemon Stream Destination Service")
app.include_router(router)

@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok", "service": "destination-service"}
