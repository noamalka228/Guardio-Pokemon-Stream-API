"""
Utility functions, rule-matching engine, and signature validation for Pokeproxy.
"""
import httpx
import hashlib
import hmac
import json
import logging
import os
from typing import Dict, List, Any, Optional
from fastapi import HTTPException
from pathlib import Path

from app.core.config import settings
from app.models.pokemon import Pokemon


logger = logging.getLogger(__name__)


def validate_signature(signature: Optional[str], raw_body: bytes) -> None:
    """
    Validates the cryptographic HMAC-SHA256 signature of the raw request body.
    Raises HTTPException (401) if signature is missing or mismatch is detected.
    """
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")

    expected_signature = hmac.new(
        settings.decoded_secret_bytes,
        raw_body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")


def load_rules() -> List[Dict[str, Any]]:
    """
    Loads routing rules from the configuration file specified in settings.
    """
    logger.info(f"Loading rules from: {settings.pokeproxy_config}")
    if not os.path.exists(settings.pokeproxy_config):
        logger.error(f"Config file not found at: {settings.pokeproxy_config}")
        raise FileNotFoundError()
    with open(settings.pokeproxy_config, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("rules", [])


def evaluate_condition(pokemon: Pokemon, condition: str) -> bool:
    """
    Evaluates a single condition string against a Pokemon object.
    Supports ==, !=, >=, <=, >, < operators and handles type conversions.
    """
    # TODO: Separate the function
    operators = ["==", "!=", ">=", "<=", ">", "<"]
    op = None
    for possible_op in operators:
        if possible_op in condition:
            op = possible_op
            break

    if not op:
        logger.warning(f"No valid operator found in condition: '{condition}'")
        return False

    parts = condition.split(op, 1)
    if len(parts) != 2:
        logger.warning(f"Invalid condition: {condition}")
        return False

    property_name = parts[0].strip()
    value_str = parts[1].strip()

    if not hasattr(pokemon, property_name):
        logger.warning(f"Pokemon object does not have attribute: '{property_name}'")
        return False

    property_value = getattr(pokemon, property_name)

    try:
        # Cast the value string to match the protobuf field value type
        if isinstance(property_value, bool):
            compare_val = value_str.lower() in ("true", "1")
        elif isinstance(property_value, (int, float)):
            compare_val = type(property_value)(value_str)
        elif isinstance(property_value, str):
            compare_val = value_str.strip("'\"")
        else:
            compare_val = value_str

        # Perform the actual comparison
        if op == "==":
            return property_value == compare_val
        elif op == "!=":
            return property_value != compare_val
        elif op == ">":
            return property_value > compare_val
        elif op == "<":
            return property_value < compare_val
        elif op == ">=":
            return property_value >= compare_val
        elif op == "<=":
            return property_value <= compare_val
    except Exception as e:
        logger.error(f"Error comparing property '{property_name}' with value '{value_str}' using '{op}': {e}")

    return False


def evaluate_rules(pokemon: Pokemon, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Evaluates all loaded rules against a Pokemon object.
    A rule matches if all of its conditions are satisfied (AND behavior).
    Returns a list of matched rules.
    """
    matched_rules = []
    for rule in rules:
        match_conditions = rule.get("match", [])
        if not match_conditions:
            continue

        all_conditions_match = True
        for cond in match_conditions:
            if not evaluate_condition(pokemon, cond):
                all_conditions_match = False
                break

        if all_conditions_match:
            matched_rules.append(rule)

    return matched_rules

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
