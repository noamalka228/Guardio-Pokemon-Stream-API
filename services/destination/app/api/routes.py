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
        pokemon, reason = body["pokemon"], body["reason"]
        logger.info(f"The Pokemon {pokemon["name"]} is {reason}!")
    except Exception as e:
        logger.error(f"Received malformed JSON body: {e}")
        return {"status": "error", "message": "Invalid JSON payload"}

    return {
        "status": "success",
        "message": f"Pokemon '{body['name']}' printed succesfully!",
    }
