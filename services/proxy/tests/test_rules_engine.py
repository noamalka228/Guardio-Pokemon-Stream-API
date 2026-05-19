"""
Unit tests for the Rules Engine Service.
"""

import pytest
from app.models.pokemon import Pokemon
from app.services.rules_engine import (
    extract_condition_parts,
    evaluate_condition,
    evaluate_rules
)


def test_extract_condition_parts():
    """
    Validates correct parsing of rules operator and values.
    """
    assert extract_condition_parts("legendary == true") == ("legendary", "==", "true")
    assert extract_condition_parts("speed > 100") == ("speed", ">", "100")
    assert extract_condition_parts("type_two != word") == ("type_two", "!=", "word")
    assert extract_condition_parts("generation < 2") == ("generation", "<", "2")
    assert extract_condition_parts("invalid_operator_string") is None


def test_evaluate_condition_equality(test_pokemon):
    """
    Validates simple equality (==) condition evaluation.
    """
    # Boolean equality
    assert evaluate_condition(test_pokemon, "legendary == true") is True
    assert evaluate_condition(test_pokemon, "legendary == false") is False
    
    # String equality
    assert evaluate_condition(test_pokemon, "type_one == Psychic") is True
    assert evaluate_condition(test_pokemon, "type_one == 'Psychic'") is True
    assert evaluate_condition(test_pokemon, "type_one == Fire") is False


def test_evaluate_condition_inequality(test_pokemon):
    """
    Validates inequality (!=) condition evaluation.
    """
    assert evaluate_condition(test_pokemon, "type_one != Psychic") is False
    assert evaluate_condition(test_pokemon, "type_one != Fire") is True
    assert evaluate_condition(test_pokemon, "legendary != false") is True


def test_evaluate_condition_greater_than(test_pokemon):
    """
    Validates greater than (>) condition evaluation.
    """
    assert evaluate_condition(test_pokemon, "speed > 100") is True
    assert evaluate_condition(test_pokemon, "speed > 130") is False
    assert evaluate_condition(test_pokemon, "speed > 150") is False


def test_evaluate_condition_less_than(test_pokemon):
    """
    Validates less than (<) condition evaluation.
    """
    assert evaluate_condition(test_pokemon, "speed < 150") is True
    assert evaluate_condition(test_pokemon, "speed < 130") is False
    assert evaluate_condition(test_pokemon, "speed < 100") is False


def test_evaluate_condition_invalid_attribute(test_pokemon):
    """
    Validates that evaluating conditions against missing attributes fails gracefully.
    """
    assert evaluate_condition(test_pokemon, "non_existent_attribute == true") is False


def test_evaluate_rules_and_logic(test_pokemon):
    """
    Validates that a rule matches only if all of its conditions match (AND logic).
    """
    rules = [
        {
            "url": "http://destination/receive",
            "reason": "high speed legendary",
            "match": [
                "legendary == true",
                "speed > 100"
            ]
        }
    ]
    matched = evaluate_rules(test_pokemon, rules)
    assert len(matched) == 1
    assert matched[0]["reason"] == "high speed legendary"


def test_evaluate_rules_partial_match_fails(test_pokemon):
    """
    Validates that a rule does not match if at least one condition fails.
    """
    rules = [
        {
            "url": "http://destination/receive",
            "reason": "failed rule",
            "match": [
                "legendary == true",
                "speed > 200"  # Mewtwo's speed is 130, so this fails
            ]
        }
    ]
    matched = evaluate_rules(test_pokemon, rules)
    assert len(matched) == 0


def test_evaluate_rules_multiple_matches(test_pokemon):
    """
    Validates that multiple matching rules are all returned.
    """
    rules = [
        {
            "url": "http://destination/receive",
            "reason": "rule 1",
            "match": ["legendary == true"]
        },
        {
            "url": "http://destination/receive",
            "reason": "rule 2",
            "match": ["speed > 100"]
        }
    ]
    matched = evaluate_rules(test_pokemon, rules)
    assert len(matched) == 2
    assert matched[0]["reason"] == "rule 1"
    assert matched[1]["reason"] == "rule 2"
