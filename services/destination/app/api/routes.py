"""
Router for minimal destination service.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/receive")
async def receive_pokemon(request: Request):
    """
    Receives JSON-formatted pokemon from the proxy service and logs it.
    """
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"Received malformed JSON body: {e}")
        return {"status": "error", "message": "Invalid JSON payload"}

    logger.info(f"Received pokemon {body['name']}")

    return {
        "status": "success",
        "message": f"Pokemon '{body['name']}' telemetry stored successfully",
        "pokemon_name": body['name']
    }
