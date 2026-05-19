"""
Helper script to start the live Pokémon stream from Guardio's hiring service.
"""
import json
import sys
import urllib.request
import urllib.error

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# Fill in your email, proxy stream endpoint URL, and Base64-encoded secret key:
# ─────────────────────────────────────────────────────────────────────────────
PROXY_URL = "https://proxy-service-6tm5.onrender.com/stream" # Streaming won't work if the PROXY_URL is not exposed to the internet.
EMAIL = "test@guard.io"
STREAM_SECRET = ""

STREAM_START_URL = "https://hiring.external.guardio.dev/be/stream_start"


def main():
    if not EMAIL:
        raise ValueError("Please set your EMAIL in start_stream.py")
        
    if not PROXY_URL:
        raise ValueError("Please set your PROXY_URL in start_stream.py")
        
    if not STREAM_SECRET:
        raise ValueError("Please set your STREAM_SECRET in start_stream.py")

    payload = {
        "url": PROXY_URL,
        "email": EMAIL,
        "enc_secret": STREAM_SECRET
    }

    print(f"Triggering Guardio Pokémon live stream to: {PROXY_URL}...")
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        STREAM_START_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode("utf-8")
            print(f"Success! Got HTTP {response.status}: {body}")
    except urllib.error.HTTPError as e:
        print(f"Failed! Got HTTP {e.code}: {e.read().decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
