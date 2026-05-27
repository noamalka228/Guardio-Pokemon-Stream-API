import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.exceptions import DestinationTimeoutError

client = TestClient(app)
app.state.rules = []


def test_stream_valid_pokemon_forwarded(
    test_pokemon_proto_bytes, generate_signature
):
    """
    Test E2E happy path: A valid Pokémon with matching rule and correct signature
    is successfully processed and forwarded to the destination service.
    """
    mock_rules = [
        {
            "url": "http://destination/receive",
            "reason": "legendary pokemon",
            "match": ["legendary == true"]
        }
    ]
    
    mock_forward_response = {
        "status": "ok",
        "message": "Pokemon Mewtwo is legendary pokemon! - printed succesfully!"
    }
    
    signature = generate_signature(test_pokemon_proto_bytes)
    
    with patch("app.api.routes.forward_pokemon", return_value=mock_forward_response) as mock_forward:
        app.state.rules = mock_rules
        response = client.post(
            "/stream",
            content=test_pokemon_proto_bytes,
            headers={"X-Grd-Signature": signature}
        )
        
        assert response.status_code == 200
        assert response.json() == mock_forward_response
        
        # Verify forward_pokemon was called with correct parameters
        mock_forward.assert_called_once()
        args = mock_forward.call_args[0]
        assert args[0] == "http://destination/receive"
        assert args[1] == "legendary pokemon"
        assert args[2]["name"] == "Mewtwo"


def test_stream_no_matching_rule_returns_404(
    test_pokemon_proto_bytes, generate_signature
):
    """
    Test that if the Pokémon does not match any configured rule, the server
    returns HTTP 404 (No matching rule found) and does not forward anything.
    """
    mock_rules = [
        {
            "url": "http://destination/receive",
            "reason": "non-legendary rule",
            "match": ["legendary == false"]
        }
    ]
    
    signature = generate_signature(test_pokemon_proto_bytes)
    
    with patch("app.api.routes.forward_pokemon") as mock_forward:
        app.state.rules = mock_rules
        response = client.post(
            "/stream",
            content=test_pokemon_proto_bytes,
            headers={"X-Grd-Signature": signature}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "No matching rule found"
        mock_forward.assert_not_called()


def test_stream_missing_signature_returns_401(test_pokemon_proto_bytes):
    """
    Test that requests without a signature header are rejected with HTTP 401.
    """
    response = client.post(
        "/stream",
        content=test_pokemon_proto_bytes
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing signature"


def test_stream_invalid_signature_returns_401(test_pokemon_proto_bytes):
    """
    Test that requests with an incorrect signature header are rejected with HTTP 401.
    """
    response = client.post(
        "/stream",
        content=test_pokemon_proto_bytes,
        headers={"X-Grd-Signature": "invalid-sig-here"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid signature"


def test_stream_malformed_protobuf_returns_400(generate_signature):
    """
    Test that malformed protobuf payload yields HTTP 400.
    """
    malformed_payload = b"not a protobuf message at all"
    signature = generate_signature(malformed_payload)
    
    response = client.post(
        "/stream",
        content=malformed_payload,
        headers={"X-Grd-Signature": signature}
    )
    assert response.status_code == 400
    assert "Failed to decode Protobuf" in response.json()["detail"]


def test_stream_destination_timeout_returns_504(
    test_pokemon_proto_bytes, generate_signature
):
    """
    Test that if the destination service times out, the proxy returns HTTP 504.
    """
    mock_rules = [
        {
            "url": "http://destination/receive",
            "reason": "legendary pokemon",
            "match": ["legendary == true"]
        }
    ]
    
    signature = generate_signature(test_pokemon_proto_bytes)
    
    with patch("app.api.routes.forward_pokemon", side_effect=DestinationTimeoutError("Timed out")):
        app.state.rules = mock_rules
        response = client.post(
            "/stream",
            content=test_pokemon_proto_bytes,
            headers={"X-Grd-Signature": signature}
        )
        
        assert response.status_code == 504
        assert response.json()["detail"] == "Pokemon Processing timed out"


def test_stream_destination_error_returns_500(
    test_pokemon_proto_bytes, generate_signature
):
    """
    Test that other unexpected errors in forwarding (e.g. 500 from client)
    return a generic HTTP 500 to protect internal details.
    """
    mock_rules = [
        {
            "url": "http://destination/receive",
            "reason": "legendary pokemon",
            "match": ["legendary == true"]
        }
    ]
    
    signature = generate_signature(test_pokemon_proto_bytes)
    
    with patch("app.api.routes.forward_pokemon", side_effect=RuntimeError("Some network error")):
        app.state.rules = mock_rules
        response = client.post(
            "/stream",
            content=test_pokemon_proto_bytes,
            headers={"X-Grd-Signature": signature}
        )
        
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal Server Error"
