from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from services.OpenRouter import OpenRouterService

from fastapi import HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

# Mount the static folder so you can open /static/index.html in the browser for testing
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root(request: Request):
    # Keep the JSON root for API users, but provide a link to the simple UI
    return {"message": "Welcome to the FastAPI application!", "ui": "/static/index.html"}

@app.get("/a2a/motivation")
@app.get("/motivation")
async def get_motivation(request: Request):
    api_key = request.headers.get("X-API-KEY")
    # If no per-request API key provided, fall back to environment variable (useful for deployments)
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return Response(content="API key missing", status_code=401)

    # Accept a user message via query parameter ?message=... (or ?q=...); use a safe default if absent
    user_message = request.query_params.get("message") or request.query_params.get("q")
    if not user_message:
        user_message = "i need motivation on programming to keep me going"

    openrouter_service = OpenRouterService(api_key=api_key)
    try:
        quote = await openrouter_service.generate_motivation(user_message=user_message)
    except Exception as e:
        # Log and return a 500-friendly message (service has its own fallbacks too)
        return Response(content=f"Error generating motivation: {e}", status_code=500)

    return {"motivation": quote}


@app.post("/a2a/motivation")
async def a2a_motivation(request: Request):
    """A2A-style POST endpoint.

    Expected JSON body (flexible):
    {
      "input": "...",
      "message": "...",
      "meta": { ... }
    }

    Returns A2A-like JSON with outputs array.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Accept multiple keys for backwards compatibility
    user_message = None
    if isinstance(payload, dict):
        user_message = payload.get("input") or payload.get("message") or payload.get("text")

    if not user_message:
        # also allow query param fallback
        user_message = request.query_params.get("message") or request.query_params.get("q")

    if not user_message:
        raise HTTPException(status_code=400, detail="No message provided in A2A payload")

    # API key can be in header or in payload.meta.api_key
    api_key = request.headers.get("X-API-KEY")
    if not api_key and isinstance(payload, dict):
        meta = payload.get("meta") or {}
        api_key = meta.get("api_key") or payload.get("api_key")

    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(status_code=401, detail="API key missing")

    service = OpenRouterService(api_key=api_key)
    try:
        quote = await service.generate_motivation(user_message=user_message)
    except Exception as e:
        # Return structured error for A2A clients
        return JSONResponse(status_code=500, content={"error": str(e)})

    response = {
        "id": "motivation_resp_1",
        "status": "success",
        "outputs": [
            {"type": "message", "content": quote}
        ]
    }

    return JSONResponse(status_code=200, content=response)

