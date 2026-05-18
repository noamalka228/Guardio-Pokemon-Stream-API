"""
Router for defining API routes.
"""
from fastapi import APIRouter, Request, HTTPException
from app.core.utils import validate_signature
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
    validate_signature(signature, raw_body)

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
