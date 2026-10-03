#!/usr/bin/env python3
"""
HITO_0.9 F0-D — Reverse Proxy Counter
======================================
Proxy HTTP que intercepta requests al provider fake, hashea cuerpos de request
(SHA-256 del body), loguea métricas y reenvía a fake_gemini.

NO modifica código productivo. Respeta Charter §5.3 (medición externa).

Uso:
    python tools/evaluation/proxy_counter.py --port 18924 --upstream http://127.0.0.1:18923 --log-file /tmp/proxy.log

Logs JSON Lines con campos:
    timestamp, method, path, body_hash, prompt_tokens, completion_tokens, 
    response_code, latency_ms
"""

import argparse
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import Response

app = FastAPI()

# Configuración global (seteada vía argumentos)
UPSTREAM_URL = "http://127.0.0.1:18923"
LOG_FILE = Path("/tmp/proxy_counter.log")


def hash_body(body: bytes) -> str:
    """SHA-256 del body de request."""
    return hashlib.sha256(body).hexdigest()


def extract_tokens(request_body: bytes) -> tuple[int, int]:
    """Extrae prompt_tokens y completion_tokens del body JSON si existe."""
    try:
        data = json.loads(request_body)
        prompt_tokens = 0
        if "contents" in data:
            for content in data["contents"]:
                if "parts" in content:
                    for part in content["parts"]:
                        if "text" in part:
                            prompt_tokens += len(part["text"]) // 4
        completion_tokens = max(10, prompt_tokens // 5)
        return prompt_tokens, completion_tokens
    except (json.JSONDecodeError, KeyError):
        return 0, 0


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(request: Request, path: str):
    """Intercepta request, hashea body, loguea, reenvía a upstream."""
    start_time = time.time()
    
    body = await request.body()
    body_hash = hash_body(body)
    prompt_tokens, completion_tokens = extract_tokens(body)
    
    upstream_url = f"{UPSTREAM_URL}/{path}"
    if request.url.query:
        upstream_url += f"?{request.url.query}"
    
    # CORRECCIÓN: Manejar response_code y headers por separado
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            upstream_response = await client.request(
                method=request.method,
                url=upstream_url,
                content=body,
                headers=dict(request.headers),
            )
            response_code = upstream_response.status_code
            response_body = upstream_response.content
            response_headers = dict(upstream_response.headers)
        except httpx.RequestError as e:
            response_code = 502
            response_body = json.dumps({"error": str(e)}).encode()
            response_headers = {}
    
    latency_ms = (time.time() - start_time) * 1000
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": request.method,
        "path": f"/{path}",
        "body_hash": body_hash,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "response_code": response_code,
        "latency_ms": round(latency_ms, 2),
    }
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    # CORRECCIÓN: Usar response_headers directamente (ya manejado el caso 502)
    return Response(
        content=response_body,
        status_code=response_code,
        headers=response_headers,
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "upstream": UPSTREAM_URL}


def main():
    parser = argparse.ArgumentParser(description="Proxy Counter for Waste T1")
    parser.add_argument("--port", type=int, default=18924, help="Port to listen on")
    parser.add_argument("--upstream", type=str, default="http://127.0.0.1:18923", 
                       help="Upstream fake_gemini URL")
    parser.add_argument("--log-file", type=str, default="/tmp/proxy_counter.log",
                       help="Path to JSON Lines log file")
    args = parser.parse_args()
    
    global UPSTREAM_URL, LOG_FILE
    UPSTREAM_URL = args.upstream
    LOG_FILE = Path(args.log_file)
    
    if LOG_FILE.exists():
        LOG_FILE.unlink()
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"[PROXY] Listening on port {args.port}, upstream={UPSTREAM_URL}")
    print(f"[PROXY] Logging to {LOG_FILE}")
    
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")


if __name__ == "__main__":
    main()