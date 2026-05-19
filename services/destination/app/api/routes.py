"""
Router for minimal destination service.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

class RecievePokemonResponse(BaseModel):
    status: str
    message: str

@router.post("/receive", response_model=RecievePokemonResponse)
async def receive_pokemon(request: Request):
    """
    Receives JSON-formatted pokemon from the proxy service and logs it.
    """
    try:
        body = await request.json()
        pokemon, reason = body["pokemon"], body["reason"]
        logger.info(f"The Pokemon {pokemon['name']} is {reason}!")
    except Exception as e:
        logger.error(f"Received malformed JSON body: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to decode JSON: {e}")

    return RecievePokemonResponse(
        status="success",
        message=f"Pokemon {pokemon['name']} is {reason} printed succesfully!"
    )
