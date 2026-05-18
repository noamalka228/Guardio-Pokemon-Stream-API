"""
Router for defining API routes.
"""
import base64
import hmac
import hashlib
import time
import httpx
from fastapi import APIRouter, Request, HTTPException, Response
from google.protobuf.json_format import MessageToDict

from app.core.config import settings
from app.schemas import pokemon_pb2

router = APIRouter()


@router.get("/", tags=["Pokemon"])
def read_root():
    """
    Returns a welcome message.
    """
    return {"message": "Welcome to Pokemon Stream API"}


@router.post("/stream", tags=["Pokemon"])
async def stream(request: Request):
    """
    Returns a stream of pokemon.
    """
    raw_body = await request.body()

    signature = request.headers.get("X-Grd-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")

    if not settings.stream_secret:
        raise HTTPException(status_code=500, detail="Server secret not configured")

    try:
        secret_bytes = base64.b64decode(settings.stream_secret)
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid server secret format")

    expected_signature = hmac.new(
        secret_bytes,
        raw_body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        pokemon = pokemon_pb2.Pokemon.FromString(raw_body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode Protobuf: {str(e)}")
        
    return {
        "message": "Pokemon received",
        "pokemon": {
            "number": pokemon.number,
            "name": pokemon.name,
            "type_one": pokemon.type_one,
            "type_two": pokemon.type_two,
            "total": pokemon.total,
            "hit_points": pokemon.hit_points,
            "attack": pokemon.attack,
            "defense": pokemon.defense,
            "special_attack": pokemon.special_attack,
            "special_defense": pokemon.special_defense,
            "speed": pokemon.speed,
            "generation": pokemon.generation,
            "legendary": pokemon.legendary
        }
    }
