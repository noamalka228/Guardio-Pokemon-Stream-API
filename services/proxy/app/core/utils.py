"""
Utility functions, rule-matching engine, and signature validation for Pokeproxy.
"""
import base64
import hashlib
import hmac
import json
import logging
import os
from typing import Dict, List, Tuple, Any, Optional
from fastapi import HTTPException

from app.core.config import settings

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
