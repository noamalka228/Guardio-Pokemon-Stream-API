# Guardio Pokémon Stream API

This project is a backend exercise built for Guardio's hiring process. The system consists of two FastAPI microservices:

- **Proxy Service** — Receives Protobuf-encoded Pokémon telemetry, validates an HMAC-SHA256 signature, evaluates the payload against configurable routing rules, and forwards matching Pokémon to the destination service.
- **Destination Service** — Receives forwarded Pokémon payloads and prints their name.

---

## Prerequisites

- Python **3.11+**
- `pip`
- Docker (optional)

---

## Running Locally

### 1. Create and activate a virtual environment

```bash
# From the repo root
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies for both services

```bash
pip install -r services/proxy/requirements.txt
pip install -r services/destination/requirements.txt
```

### 3. Configure the Proxy environment

Copy the example env file and fill in the values:

```bash
cp services/proxy/.env.example services/proxy/.env
```

Edit `services/proxy/.env`:
**NOTE**: The pokeproxy config path should be absolute.

```env
POKEPROXY_CONFIG="<absolute_path_to_config_file>"
STREAM_SECRET=<base64_encoded_secret_key>
```

| Variable           | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| `POKEPROXY_CONFIG` | Absolute path to the JSON rules config file (use `config-local.json` locally) |
| `STREAM_SECRET`    | A Base64-encoded HMAC-SHA256 secret used to validate incoming request signatures |

### 4. Start the Destination service

Open a terminal and run:

```bash
cd services/destination
uvicorn app.main:app --port 8001
```

### 5. Start the Proxy service

Open a second terminal and run:

```bash
cd services/proxy
uvicorn app.main:app --port 8002
```

Both services will hot-reload automatically when source files change.

---

## Running with Docker

Using docker-compose.yml file you can simply start both services by running:

```bash

docker-compose up -d

```

## Routing Rules Configuration

The proxy evaluates each incoming Pokémon against a JSON rules file. A Pokémon is forwarded only if it matches **all conditions** in a rule (AND logic).

**Example `config-local.json`:**

```json
{
  "rules": [
    {
      "url": "http://localhost:8001/receive",
      "reason": "legendary pokemon",
      "match": ["legendary == true"]
    },
    {
      "url": "http://localhost:8001/receive",
      "reason": "high speed pokemon",
      "match": ["speed > 100"]
    },
    {
      "url": "http://localhost:8001/receive",
      "reason": "awesome pokemon",
      "match": [
        "hit_points == 20",
        "special_defense > 10",
        "generation < 20"
      ]
    }
  ]
}
```

**Supported operators:** `==`, `!=`, `>`, `<`

**Matchable fields** (from the Pokémon Protobuf schema):

| Field             | Type    |
|-------------------|---------|
| `number`          | int     |
| `name`            | string  |
| `type_one`        | string  |
| `type_two`        | string  |
| `total`           | int     |
| `hit_points`      | int     |
| `attack`          | int     |
| `defense`         | int     |
| `special_attack`  | int     |
| `special_defense` | int     |
| `speed`           | int     |
| `generation`      | int     |
| `legendary`       | bool    |

---

## API Endpoints

### Proxy Service (`http://localhost:8002`)

| Method | Path      | Description                                      |
|--------|-----------|--------------------------------------------------|
| `GET`  | `/`       | Welcome message                                  |
| `GET`  | `/health` | Health check                                     |
| `POST` | `/stream` | Receives Protobuf Pokémon payload, validates signature, evaluates rules, forwards match |

**Required request headers for `/stream`:**

| Header              | Value                                          |
|---------------------|------------------------------------------------|
| `Content-Type`      | `application/x-protobuf`                       |
| `X-Grd-Signature`   | HMAC-SHA256 hex digest of the raw request body |

**Response codes:**

| Code | Meaning                                      |
|------|----------------------------------------------|
| `200` | Pokémon matched a rule and was forwarded successfully |
| `401` | Missing or invalid HMAC signature            |
| `400` | Request body could not be decoded as Protobuf |
| `404` | No rule matched the Pokémon                  |
| `500` | Internal forwarding error                    |
