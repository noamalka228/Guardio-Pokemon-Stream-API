FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt .
RUN apt-get update && apt-get install -y dos2unix && \
    dos2unix requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
