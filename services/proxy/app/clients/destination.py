"""
HTTP Client for forwarding Pokemon telemetry data to the destination service.
"""
import httpx
import logging
from typing import Dict, Any
from fastapi import HTTPException

logger = logging.getLogger(__name__)


async def forward_pokemon(url: str, reason: str, pokemon_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forwards the Pokemon telemetry data to the destination URL.
    Returns the response JSON dictionary from the destination service.
    """
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "pokemon": pokemon_data,
                "reason": reason
            }
            logger.info(f"Forwarding pokemon to {url}: Status {payload}")
            response = await client.post(url, json=payload, timeout=5.0)
            response.raise_for_status()
            logger.info(f"Successfully forwarded pokemon to {url}: Status {response.status_code}")
            return response.json()
    except Exception as e:
        logger.error(f"Error occurred while forwarding pokemon to {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to forward pokemon to {url}")
