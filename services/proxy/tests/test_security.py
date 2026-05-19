"""
Unit tests for security.
"""

import pytest
from fastapi import HTTPException
from app.core.security import validate_signature


def test_valid_signature_passes(generate_signature):
    """
    Validates that a correct HMAC signature does not raise an exception.
    """
    body = b"some pokemon stream data"
    signature = generate_signature(body)
    
    # Should run without raising any error
    validate_signature(signature, body)


def test_missing_signature_raises_401():
    """
    Validates that a missing signature throws an HTTP 401.
    """
    body = b"some data"
    with pytest.raises(HTTPException) as exc_info:
        validate_signature(None, body)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Missing signature"


def test_invalid_signature_raises_401(generate_signature):
    """
    Validates that an invalid signature throws an HTTP 401.
    """
    body = b"some data"
    wrong_body = b"some other data"
    wrong_signature = generate_signature(wrong_body)
    
    with pytest.raises(HTTPException) as exc_info:
        validate_signature(wrong_signature, body)
        
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid signature"
