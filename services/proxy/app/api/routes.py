"""
Router for defining Pokemon Proxy Stream Service API routes.
"""
import logging
from fastapi import APIRouter, Request, HTTPException
from app.core.utils import (
    validate_signature,
    load_rules,
    evaluate_rules,
    forward_pokemon
)
from app.proto import pokemon_pb2
from app.models.pokemon import Pokemon
from app.models.rule import Rule
from google.protobuf.message import DecodeError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", tags=["Pokemon"])
def read_root():
    """
    Returns a welcome message.
    """
    return {"message": "Welcome to Pokemon Stream API"}


@router.post("/stream", tags=["Pokemon"])
async def stream(request: Request):
    """
    Receives a stream of Pokemon data, validates the signature, evaluates rules, 
    and forwards the data to the destination service.
    The destination service will process the data and return a response to the 
    proxy service and eventually to the client.
    """
    raw_body = await request.body()

    signature = request.headers.get("X-Grd-Signature")
    validate_signature(signature, raw_body)

    try:
        proto_pokemon = pokemon_pb2.Pokemon.FromString(raw_body)
        pokemon = Pokemon.from_proto(proto_pokemon)

        rules = load_rules()
        matched_rules = evaluate_rules(pokemon, rules)
        if not matched_rules:
            raise HTTPException(status_code=404, detail="No matching rule found")

        # TODO: Consider using gRPC instead of HTTP for forwarding
        # Maybe randomize the rule that gets matched
        selected_rule: Rule = matched_rules[0]
        logger.info(f"Found {len(matched_rules)} matching rules for pokemon: {pokemon.name}")
        logger.info(f"Forwading to {selected_rule['url']} with reason: {selected_rule['reason']}")
        return await forward_pokemon(selected_rule["url"], selected_rule["reason"], pokemon.to_dict())
        
    except DecodeError as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode Protobuf: {str(e)}")
    except HTTPException as e:
        # TODO: I dont like this
        raise e
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
