"""
Rule matching engine for evaluating Pokemon telemetry data against dynamic conditions.
"""
import os
import json
import logging
from typing import List, Dict, Any

from app.core.config import settings
from app.models.pokemon import Pokemon

logger = logging.getLogger(__name__)


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


def extract_condition_parts(condition: str) -> tuple[str, str, str] | None:
    """
    Extracts the property name, operator, and value from a condition string.
    """
    operators = ["==", "!=", ">", "<"]
    op = None
    for possible_op in operators:
        if possible_op in condition:
            op = possible_op
            break

    if not op:
        logger.warning(f"No valid operator found in condition: '{condition}'")
        return None

    parts = condition.split(op, 1)
    if len(parts) != 2:
        logger.warning(f"Invalid condition: {condition}")
        return None

    return parts[0].strip(), op, parts[1].strip()


def evaluate_condition(pokemon: Pokemon, condition: str) -> bool:
    """
    Evaluates a single condition string against a Pokemon object.
    Supports ==, !=, >, < operators and handles type conversions.
    """
    parts = extract_condition_parts(condition)
    if not parts:
        return False

    property_name, op, property_value = parts

    if not hasattr(pokemon, property_name):
        logger.warning(f"Pokemon object does not have attribute: '{property_name}'")
        return False

    property_value = getattr(pokemon, property_name)

    try:
        # Cast the value string to match the protobuf field value type
        if isinstance(property_value, bool):
            compare_value = property_value.lower() in ("true", "1")
        elif isinstance(property_value, (int, float)):
            compare_value = type(property_value)(property_value)
        elif isinstance(property_value, str):
            compare_value = property_value.strip("'\"")
        else:
            compare_value = property_value

        # Perform the actual comparison
        if op == "==":
            return property_value == compare_value
        elif op == "!=":
            return property_value != compare_value
        elif op == ">":
            return property_value > compare_value
        elif op == "<":
            return property_value < compare_value
    except Exception as e:
        logger.error(f"Error comparing property '{property_name}' with value '{property_value}' using '{op}': {e}")

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
