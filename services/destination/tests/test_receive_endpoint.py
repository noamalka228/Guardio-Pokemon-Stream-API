"""
Unit tests for the Destination Service /receive endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "pokemon": {
        "number": 150,
        "name": "Mewtwo",
        "type_one": "Psychic",
        "type_two": "",
        "total": 680,
        "hit_points": 106,
        "attack": 110,
        "defense": 90,
        "special_attack": 154,
        "special_defense": 90,
        "speed": 130,
        "generation": 1,
        "legendary": True
    },
    "reason": "legendary pokemon"
}


def test_receive_valid_pokemon_returns_200():
    """
    Test happy path: A valid JSON payload is accepted and returns 200
    with the expected status and message fields.
    """
    response = client.post("/receive", json=VALID_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["message"] == "Pokemon Mewtwo is legendary pokemon! - printed succesfully!"


def test_receive_malformed_json_returns_400():
    """
    Test that sending a malformed JSON payload (missing required keys)
    results in a 400 Bad Request.
    """
    malformed_payload = {"wrong_key": "wrong_value"}

    response = client.post("/receive", json=malformed_payload)

    assert response.status_code == 400
    assert "Failed to decode JSON" in response.json()["detail"]
