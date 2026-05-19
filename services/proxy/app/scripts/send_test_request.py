"""
Helper script to send a manual test request containing a signed Protobuf Pokémon
to the running Proxy Service.
"""
import os
import sys
import base64
import hashlib
import hmac
import urllib.request
import urllib.error
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from app.proto import pokemon_pb2

env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path=env_path)


def main():
    url = "http://localhost:8002/stream"
    secret_b64 = os.environ.get("STREAM_SECRET")
    if not secret_b64:
        raise ValueError("STREAM_SECRET is not set in environment or .env file.")

    print(f"Target URL:     {url}")
    print(f"Using Secret:   {secret_b64}")

    pokemon = pokemon_pb2.Pokemon()
    pokemon.number = 150
    pokemon.name = "Mewtwo"
    pokemon.type_one = "Psychic"
    pokemon.total = 680
    pokemon.hit_points = 106
    pokemon.attack = 110
    pokemon.defense = 90
    pokemon.special_attack = 154
    pokemon.special_defense = 90
    pokemon.speed = 130
    pokemon.generation = 1
    pokemon.legendary = True

    body = pokemon.SerializeToString()
    secret_bytes = base64.b64decode(secret_b64)
    signature = hmac.new(secret_bytes, body, hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/x-protobuf",
        "X-Grd-Signature": signature
    }

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    print("\nSending Pokémon request to proxy...")
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Success! Status: {response.status}")
            print(f"Response Body: {response.read().decode('utf-8')}")
    except urllib.error.HTTPError as e:
        print(f"Failed! Status: {e.code}")
        print(f"Response Body: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
