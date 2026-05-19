"""
Conftest for Proxy Service Tests
"""

import base64
import hashlib
import hmac
import pytest
from app.core.config import settings
from app.models.pokemon import Pokemon
from app.proto import pokemon_pb2

TEST_SECRET_BASE64 = "q/8V0xH+hP7LzKjB4cRt1sW6Yv2N9uA5iE0O3fD1m/A="
TEST_SECRET_BYTES = base64.b64decode(TEST_SECRET_BASE64)


@pytest.fixture(scope="session", autouse=True)
def mock_settings():
    """
    Autouse session fixture to ensure settings always point to test values
    and do not rely on local environment files.
    """
    settings.stream_secret = TEST_SECRET_BASE64
    settings.pokeproxy_config = "test-config.json"
    yield


@pytest.fixture
def generate_signature():
    """
    Fixture helper to generate the HMAC signature for any raw body bytes.
    """
    def _sign(body: bytes) -> str:
        return hmac.new(
            TEST_SECRET_BYTES,
            body,
            hashlib.sha256
        ).hexdigest()
    return _sign


@pytest.fixture
def test_pokemon_data():
    """
    Fixture returning standard dictionary representation of a Pokémon.
    """
    return {
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
    }


@pytest.fixture
def test_pokemon(test_pokemon_data):
    """
    Fixture returning a Pokemon dataclass model instance.
    """
    return Pokemon(**test_pokemon_data)


@pytest.fixture
def test_pokemon_proto_bytes(test_pokemon_data):
    """
    Fixture returning Protobuf serialized bytes for the test Pokémon.
    """
    proto = pokemon_pb2.Pokemon()
    for key, val in test_pokemon_data.items():
        setattr(proto, key, val)
    return proto.SerializeToString()
