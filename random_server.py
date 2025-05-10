#just a simple random server load balancer
# this one is a simple random load balancer

from fastapi import FastAPI, Request, HTTPException
import httpx
import json
import random
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)

global_client = httpx.AsyncClient(timeout=10.0)

@app.on_event("shutdown")
async def shutdown_event():
    await global_client.aclose()

# Load backend URLs
with open("servers.json") as f:
    servers = json.load(f)
server_urls = [s["url"] for s in servers]

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(path: str, request: Request):
    body = await request.body()
    method = request.method
    headers = request.headers.raw

    # here we randomly choose a backend
    backend_url = random.choice(server_urls)
    target_url = f"{backend_url}/{path}"

    try:
        resp = await global_client.request(
            method,
            target_url,
            headers=headers,
            content=body
        )
        if resp.status_code >= 500:
            raise HTTPException(status_code=502, detail=f"Upstream error: {resp.status_code}")
    except httpx.RequestError as e:
        # network or timeout error
        raise HTTPException(status_code=502, detail=str(e))

    return resp.json()
