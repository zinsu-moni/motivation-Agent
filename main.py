from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from services.OpenRouter import OpenRouterService

from fastapi import HTTPException
from fastapi.responses import JSONResponse
import json
from pathlib import Path
import logging

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
    # Robust parsing: accept JSON, form-encoded, or raw text bodies.
    logger = logging.getLogger(__name__)
    payload = None
    raw_body = None
    content_type = (request.headers.get('content-type') or '').lower()
    try:
        if 'application/json' in content_type:
            payload = await request.json()
        elif 'application/x-www-form-urlencoded' in content_type or 'multipart/form-data' in content_type:
            form = await request.form()
            # form is a starlette.datastructures.FormData; convert to dict
            payload = {k: v for k, v in form.items()}
        else:
            # try JSON first, then fall back to raw text
            try:
                payload = await request.json()
            except Exception:
                raw_bytes = await request.body()
                raw_body = raw_bytes.decode('utf-8', errors='replace')
                # try to parse raw text as JSON
                try:
                    payload = json.loads(raw_body)
                except Exception:
                    # treat raw body as message text
                    payload = {"input": raw_body}
    except Exception:
        # Log raw body snippet for debugging (masked)
        try:
            raw = (await request.body()).decode('utf-8', errors='replace')
            snippet = raw[:1000]
            logger.info('Received invalid A2A body (could not parse): %s', snippet)
        except Exception:
            logger.debug('Failed to read raw body for logging')
        raise HTTPException(status_code=400, detail="Invalid request payload")

    # Sanitize payload for logging (mask api keys)
    try:
        sanitized = dict(payload) if isinstance(payload, dict) else payload
        if isinstance(sanitized, dict):
            meta = sanitized.get('meta')
            if isinstance(meta, dict) and 'api_key' in meta:
                meta['api_key'] = '***masked***'
            if 'api_key' in sanitized:
                sanitized['api_key'] = '***masked***'
        logger.info('Received A2A payload: %s', sanitized)
    except Exception:
        logger.debug('Failed to sanitize A2A payload for logging')

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


@app.get("/workflow")
async def get_workflow():
    """Return the workflow JSON so you can confirm the deployed workflow."""
    p = Path("workflow/workflow.json")
    if not p.exists():
        raise HTTPException(status_code=404, detail="workflow.json not found")
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
        return JSONResponse(status_code=200, content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read workflow.json: {e}")


@app.get("/health")
async def health():
    """Simple health endpoint reporting key presence, service init and workflow active flag."""
    api_key = os.getenv("OPENAI_API_KEY")
    key_present = bool(api_key)
    wf_path = Path("workflow/workflow.json")
    wf_active = False
    wf_id = None
    if wf_path.exists():
        try:
            wf = json.loads(wf_path.read_text(encoding='utf-8'))
            wf_active = bool(wf.get('active'))
            wf_id = wf.get('id')
        except Exception:
            wf_active = False

    # Try to initialize the service (won't call external API) to detect gross misconfigurations
    service_init_ok = False
    try:
        _ = OpenRouterService(api_key=api_key)
        service_init_ok = True
    except Exception as e:
        logging.getLogger(__name__).warning('Service init failed: %s', e)

    return JSONResponse(status_code=200, content={
        "ok": True,
        "api_key_present": key_present,
        "service_init_ok": service_init_ok,
        "workflow_active": wf_active,
        "workflow_id": wf_id
    })

