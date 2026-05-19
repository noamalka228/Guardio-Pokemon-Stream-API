"""
HTTP Client for forwarding Pokemon telemetry data to the destination service.
"""
import httpx
import logging
from typing import Dict, Any
from app.exceptions import DestinationTimeoutError

logger = logging.getLogger(__name__)


async def forward_pokemon(url: str, reason: str, pokemon_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forwards the Pokemon telemetry data to the destination URL.
    Returns the response JSON dictionary from the destination service.
    """
    # Implemented an HTTP-based communication between the proxy and destination service
    # for simplicity and readability purposes. In a real-world scenario, consider using gRPC
    # for better performance.
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
    except httpx.TimeoutException:
        logger.error(f"Timed out while forwarding pokemon to {url}")
        raise DestinationTimeoutError(f"Destination service timed out: {url}")
    except Exception as e:
        logger.error(f"Error occurred while forwarding pokemon to {url}: {e}")
        raise RuntimeError(f"Failed to forward pokemon to {url}") from e
