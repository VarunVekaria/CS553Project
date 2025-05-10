#this one is a simple round robin load balancer
# we have used fastapi and httpx   
# using prometheus for metrics
# using json for configuration
# using httpx for async requests
# using fastapi for to create the proxy server
# using prometheus_fastapi_instrumentator for metrics


from fastapi import FastAPI, Request
import httpx
import json
from threading import Lock
from prometheus_fastapi_instrumentator import Instrumentator
import psutil

app = FastAPI()
Instrumentator().instrument(app).expose(app)

client = httpx.AsyncClient(timeout=10.0)

with open("servers.json") as f:
    servers = json.load(f)
server_urls = [s["url"] for s in servers]

last_index = -1
lock = Lock()

def get_next_server():
    global last_index
    with lock:
        last_index = (last_index + 1) % len(server_urls)
        return server_urls[last_index]

@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()

@app.api_route("/{path:path}", methods=["GET","POST","PUT","DELETE","PATCH"])
async def proxy(path: str, request: Request):
    backend_url = get_next_server()
    full_url = f"{backend_url}/{path}"

    # forward using the *same* client (reuses sockets)
    response = await client.request(
        request.method,
        full_url,
        headers=request.headers.raw,
        content=await request.body()
    )
    return response.json()

@app.get("/metrics")
async def metrics():
    return {
        "cpu": psutil.cpu_percent(interval=None),
        "mem": psutil.virtual_memory().percent
    }
