"""
Mock Destination Service for receiving matched Pokemon requests.
"""
import logging
from fastapi import FastAPI, Request, Header
from typing import Optional

# Set up logging to show in console/Docker logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("destination-service")

app = FastAPI(title="Pokemon Stream Destination Service")


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok", "service": "destination-service"}
