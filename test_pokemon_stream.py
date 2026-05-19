#!/usr/bin/env python3
"""
End-to-end integration test suite to verify the Pokemon Stream API rule engine.
Tests multiple Pokemon cases, signature validation, and payload validation.
"""
import os
import sys
import base64
import hmac
import hashlib
import json
import urllib.request
import urllib.error

# Setup path so we can import the generated Protobuf schema
sys.path.append(os.path.join(os.path.dirname(__file__), "services", "proxy"))
try:
    from app.proto import pokemon_pb2
except ImportError as e:
    print("\033[91m[ERROR] Failed to import app.proto.pokemon_pb2.\033[0m")
    print("Please make sure the proxy service directory structure is correct.")
    print(f"Details: {e}")
    sys.exit(1)


def load_stream_secret() -> str:
    """Reads stream secret from services/proxy/.env if present."""
    env_path = os.path.join(os.path.dirname(__file__), "services", "proxy", ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("STREAM_SECRET="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    
    # Fallback default
    return "q/8V0xH+hP7LzKjB4cRt1sW6Yv2N9uA5iE0O3fD1m/A="


def calculate_signature(secret_b64: str, body: bytes) -> str:
    """Computes HMAC-SHA256 signature of body using base64-decoded secret."""
    secret_bytes = base64.b64decode(secret_b64)
    return hmac.new(secret_bytes, body, hashlib.sha256).hexdigest()


def send_request(url: str, headers: dict, data: bytes) -> tuple:
    """Sends a binary POST request and returns (status_code, response_body_text)."""
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except urllib.error.URLError as e:
        return 0, f"Connection Failed: {e.reason}"


def build_pokemon(number, name, type_one, type_two, total, hp, attack, defense, sp_attack, sp_defense, speed, gen, legendary):
    """Factory function to build a Protobuf Pokemon object."""
    pokemon = pokemon_pb2.Pokemon()
    pokemon.number = number
    pokemon.name = name
    pokemon.type_one = type_one
    pokemon.type_two = type_two
    pokemon.total = total
    pokemon.hit_points = hp
    pokemon.attack = attack
    pokemon.defense = defense
    pokemon.special_attack = sp_attack
    pokemon.special_defense = sp_defense
    pokemon.speed = speed
    pokemon.generation = gen
    pokemon.legendary = legendary
    return pokemon


def run_all_tests():
    # url = "https://proxy-service-6tm5.onrender.com/stream"
    url = "http://localhost:8002/stream"
    secret_b64 = load_stream_secret()
    
    print("\n" + "=" * 70)
    print("           POKEMON STREAM API - END-TO-END FLOW TEST RUNNER")
    print("=" * 70)
    print(f"Active Base64 Secret: {secret_b64}")
    print(f"Target Proxy URL:     {url}")
    print("=" * 70)

    # 1. Define Pokemon Test Cases
    pokemon_cases = [
        {
            "name": "Mewtwo (Legendary + High Speed)",
            "obj": build_pokemon(150, "Mewtwo", "Psychic", "", 680, 106, 110, 90, 154, 90, 130, 1, True),
            "expected_status": 200,
            "description": "Matches 'legendary == true' and 'speed > 100'. Should forward successfully."
        },
        {
            "name": "Greninja (Non-Legendary, High Speed)",
            "obj": build_pokemon(658, "Greninja", "Water", "Dark", 530, 72, 95, 67, 103, 71, 122, 6, False),
            "expected_status": 200,
            "description": "Matches 'speed > 100' rule. Should forward successfully."
        },
        {
            "name": "Shuckle (Non-Legendary, Awesome Stats)",
            "obj": build_pokemon(213, "Shuckle", "Bug", "Rock", 505, 20, 10, 230, 10, 230, 5, 2, False),
            "expected_status": 200,
            "description": "Matches 'awesome pokemon' rule (HP=20, SP_DEF > 10). Should forward successfully."
        },
        {
            "name": "Pikachu (No Rules Matched)",
            "obj": build_pokemon(25, "Pikachu", "Electric", "", 320, 35, 55, 40, 50, 50, 90, 1, False),
            "expected_status": 404,
            "description": "Does not match any rule. Should be blocked with 404 Not Found."
        },
        {
            "name": "Bulbasaur (No Rules Matched)",
            "obj": build_pokemon(1, "Bulbasaur", "Grass", "Poison", 318, 45, 49, 49, 65, 65, 45, 1, False),
            "expected_status": 404,
            "description": "Does not match any rule. Should be blocked with 404 Not Found."
        }
    ]

    total_tests = 0
    passed_tests = 0

    # ----------------------------------------------------
    # PHASE 1: TESTING POKEMON STREAM RULES
    # ----------------------------------------------------
    print("\n--- PHASE 1: TELEMETRY STREAM & RULE MATCHING TESTS ---")
    for case in pokemon_cases:
        total_tests += 1
        name = case["name"]
        pokemon_pb = case["obj"]
        expected = case["expected_status"]
        desc = case["description"]
        
        print(f"\n[TEST] Sending {name}...")
        print(f"       Details: {desc}")
        
        raw_body = pokemon_pb.SerializeToString()
        sig = calculate_signature(secret_b64, raw_body)
        headers = {
            "Content-Type": "application/x-protobuf",
            "X-Grd-Signature": sig
        }
        
        status, response_text = send_request(url, headers, raw_body)
        
        if status == expected:
            print(f"\033[92m[PASS] Got HTTP {status} as expected!\033[0m")
            print(f"       Response: {response_text.strip()}")
            passed_tests += 1
        else:
            print(f"\033[91m[FAIL] Got HTTP {status}, but expected {expected}.\033[0m")
            print(f"       Response: {response_text.strip()}")

    # ----------------------------------------------------
    # PHASE 2: SECURITY & VALIDATION TESTS
    # ----------------------------------------------------
    print("\n--- PHASE 2: SECURITY & VALIDATION TESTS ---")
    
    # Test case 2.1: Missing Signature
    total_tests += 1
    print("\n[TEST] Sending Mewtwo with MISSING signature header...")
    pikachu_pb = pokemon_cases[3]["obj"]
    raw_body = pikachu_pb.SerializeToString()
    headers = {"Content-Type": "application/x-protobuf"}
    status, response_text = send_request(url, headers, raw_body)
    if status == 401:
        print(f"\033[92m[PASS] Got HTTP {status} (Blocked missing signature) as expected!\033[0m")
        print(f"       Response: {response_text.strip()}")
        passed_tests += 1
    else:
        print(f"\033[91m[FAIL] Got HTTP {status}, but expected 401.\033[0m")
        print(f"       Response: {response_text.strip()}")

    # Test case 2.2: Invalid Signature
    total_tests += 1
    print("\n[TEST] Sending Mewtwo with INVALID signature header...")
    headers = {
        "Content-Type": "application/x-protobuf",
        "X-Grd-Signature": "wronghmacsigvalueabc123"
    }
    status, response_text = send_request(url, headers, raw_body)
    if status == 401:
        print(f"\033[92m[PASS] Got HTTP {status} (Blocked invalid signature) as expected!\033[0m")
        print(f"       Response: {response_text.strip()}")
        passed_tests += 1
    else:
        print(f"\033[91m[FAIL] Got HTTP {status}, but expected 401.\033[0m")
        print(f"       Response: {response_text.strip()}")

    # Test case 2.3: Malformed Protobuf Payload
    total_tests += 1
    print("\n[TEST] Sending malformed Protobuf bytes payload...")
    bad_bytes = b"\x08\x01\x12\x04Bad\x1a\x07Bytes!!"
    sig = calculate_signature(secret_b64, bad_bytes)
    headers = {
        "Content-Type": "application/x-protobuf",
        "X-Grd-Signature": sig
    }
    status, response_text = send_request(url, headers, bad_bytes)
    if status == 400:
        print(f"\033[92m[PASS] Got HTTP {status} (Blocked decode error) as expected!\033[0m")
        print(f"       Response: {response_text.strip()}")
        passed_tests += 1
    else:
        print(f"\033[91m[FAIL] Got HTTP {status}, but expected 400.\033[0m")
        print(f"       Response: {response_text.strip()}")

    # ----------------------------------------------------
    # RESULTS SUMMARY
    # ----------------------------------------------------
    print("\n" + "=" * 70)
    print("                          FLOW TEST SUMMARY")
    print("=" * 70)
    print(f"  Passed Tests: {passed_tests} / {total_tests}")
    if passed_tests == total_tests:
        print("\033[92m  ALL END-TO-END FLOW TESTS COMPLETED SUCCESSFULLY!\033[0m")
    else:
        print("\033[91m  SOME FLOW TESTS FAILED. PLEASE VERIFY SERVICE LOGS.\033[0m")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_all_tests()
