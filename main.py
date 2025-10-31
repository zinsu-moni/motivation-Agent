from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from services.OpenRouter import OpenRouterService
import uuid
import asyncio
import httpx
from datetime import datetime

from fastapi import HTTPException
from fastapi.responses import JSONResponse
import json
from pathlib import Path
import logging

app = FastAPI()

# Allow CORS for development/testing so agent pages served from other origins can receive replies
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def clean_motivation(text: str) -> str:
    """Heuristic cleaner: remove common preamble phrases and return up to 3 sentences.

    This helps remove model lead-ins like "You're seeking..." so callers get the actual motivational text.
    """
    if not text:
        return text

    import re

    # Normalize whitespace
    t = re.sub(r"\s+", " ", text).strip()

    # Remove common preamble patterns
    preamble_patterns = [
        r"^it\s?sounds like\b.*?[.?!]\s*",
        r"^you('?re| are)\s+seeking\b.*?[.?!]\s*",
        r"^it\s+looks\s+like\b.*?[.?!]\s*",
        r"^you\s+want\b.*?[.?!]\s*",
        r"^you\s+are\s+looking\s+for\b.*?[.?!]\s*",
        r"^i\s+understand\b.*?[.?!]\s*",
    ]
    for pat in preamble_patterns:
        t = re.sub(pat, "", t, flags=re.IGNORECASE)

    # Split into sentences (very simple heuristic)
    sentences = re.split(r'(?<=[.!?])\s+', t)
    # Keep up to first 3 non-empty sentences
    kept = []
    for s in sentences:
        s = s.strip()
        if s:
            kept.append(s)
        if len(kept) >= 3:
            break

    return " ".join(kept) if kept else t

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
        logging.getLogger(__name__).info('Calling generate_motivation for message (truncated): %s', (user_message or '')[:200])
        quote = await openrouter_service.generate_motivation(user_message=user_message)
        # Clean model preamble and limit to concise reply
        try:
            quote = clean_motivation(quote)
        except Exception:
            pass
        logging.getLogger(__name__).info('Received quote (truncated): %s', (quote or '')[:200])
    except Exception as e:
        # Log and return a 500-friendly message (service has its own fallbacks too)
        logging.getLogger(__name__).exception('generate_motivation failed: %s', e)
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
    rpc_id = None
    is_jsonrpc = False
    if isinstance(payload, dict):
        # Handle JSON-RPC style payloads (e.g., telex/mastra)
        if payload.get('jsonrpc') and isinstance(payload.get('params'), dict):
            is_jsonrpc = True
            rpc_id = payload.get('id')
            try:
                msg = payload['params'].get('message') or {}
                # message.parts is a list of {kind: 'text', text: '...'}
                parts = msg.get('parts') or []
                texts = []
                for p in parts:
                    if isinstance(p, dict) and p.get('kind') == 'text' and p.get('text'):
                        texts.append(p.get('text'))
                    elif isinstance(p, str):
                        texts.append(p)
                if texts:
                    user_message = ' '.join(texts).strip()
                # fallback to message.messageId or other fields
                if not user_message:
                    user_message = msg.get('text') or msg.get('content')
            except Exception:
                user_message = None
        else:
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
        # Post-process the model output to remove preamble and keep it concise for A2A callers
        try:
            cleaned = clean_motivation(quote)
        except Exception:
            cleaned = quote
        logging.getLogger(__name__).info('Generated motivation (truncated): %s', (cleaned or '')[:200])
    except Exception as e:
        # Return structured error for A2A clients
        return JSONResponse(status_code=500, content={"error": str(e)})

    # Build a stable response id: prefer the incoming RPC id when present, otherwise generate one
    resp_id = None
    try:
        resp_id = rpc_id or f"resp_{uuid.uuid4().hex}"
    except Exception:
        resp_id = f"resp_{uuid.uuid4().hex}"

    response = {
        "id": resp_id,
        "status": "success",
        "outputs": [
            {
                "type": "message",
                "content": cleaned,
                # Provide a `message`/`parts` shape which many A2A controllers expect
                "message": {"parts": [{"kind": "text", "text": cleaned}]}
            }
        ]
    }

    # Best-effort push callback: if caller provided a pushNotificationConfig.url, POST the result to it.
    try:
        push_url = None
        pnc = {}
        if isinstance(payload, dict):
            params = payload.get('params') or {}
            config = params.get('configuration') or {}
            pnc = config.get('pushNotificationConfig') or {}
            push_url = pnc.get('url')

        if push_url:
            async def _post_push(url: str, body: dict, pnc_config: dict, logger=logging.getLogger(__name__)):
                last = {
                    "ts": datetime.utcnow().isoformat() + 'Z',
                    "url": url,
                    "status": None,
                    "resp": None,
                    "error": None
                }
                try:
                    # Determine headers: allow bearer token or custom headers if provided in pnc
                    headers = {"Content-Type": "application/json"}
                    # Common token locations
                    auth = pnc_config.get('authentication') or {}
                    token = None
                    # Look for obvious token names
                    for k in ('token', 'accessToken', 'access_token', 'bearer', 'api_key', 'key'):
                        if isinstance(auth, dict) and auth.get(k):
                            token = auth.get(k)
                            break
                    # Also check top-level pnc_config for 'token' keys
                    if not token:
                        for k in ('token', 'accessToken', 'access_token', 'bearer', 'api_key', 'key'):
                            if pnc_config.get(k):
                                token = pnc_config.get(k)
                                break
                    if token:
                        headers['Authorization'] = f"Bearer {token}"
                    # Allow additional headers forwarded from pnc_config.headers
                    extra_headers = pnc_config.get('headers') or {}
                    if isinstance(extra_headers, dict):
                        headers.update(extra_headers)

                    logger.info('Posting push notification to %s', url)
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        resp = await client.post(url, json=body, headers=headers)
                        last['status'] = resp.status_code
                        last['resp'] = (resp.text or '')[:1000]
                        logger.info('Push notification posted: %s %s', resp.status_code, last['resp'][:300])
                except Exception as e:
                    last['error'] = str(e)
                    logger.exception('Failed to post push notification to %s: %s', url, e)
                # store the last push attempt in-memory for quick diagnostics
                try:
                    _LAST_PUSH['last'] = last
                except Exception:
                    logger.debug('Failed to record last push status')

            # Create push body that controllers commonly expect (mirrors the returned result)
            push_body = {
                "jsonrpc": "2.0",
                "id": resp_id,
                "result": response
            }

            # Ensure global store exists
            try:
                _LAST_PUSH
            except NameError:
                _LAST_PUSH = {}

            # Fire-and-forget the push so we don't block the A2A response; log will capture failures
            try:
                asyncio.create_task(_post_push(push_url, push_body, pnc))
            except Exception:
                # Fallback: call without awaiting (best-effort)
                _ = _post_push(push_url, push_body, pnc)
    except Exception:
        logging.getLogger(__name__).exception('Error preparing push notification')

    # If the caller used JSON-RPC, reply with a JSON-RPC style response
    if is_jsonrpc:
        rpc_resp = {
            "jsonrpc": "2.0",
            "id": resp_id,
            "result": response
        }
        logging.getLogger(__name__).info('Returning JSON-RPC response id=%s (truncated output): %s', resp_id, (cleaned or '')[:200])
        return JSONResponse(status_code=200, content=rpc_resp)

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


@app.get("/diag/openrouter")
async def diag_openrouter():
    """Diagnostic endpoint: make a quick test call from the host environment to validate provider auth.

    Returns a short sample response or the exact error to help debug 401/permission problems.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return JSONResponse(status_code=400, content={"ok": False, "error": "OPENAI_API_KEY not set in environment"})

    svc = OpenRouterService(api_key=api_key)
    try:
        sample = await svc.generate_motivation(user_message="test authentication ping")
        # return a short snippet so logs don't leak large content
        return JSONResponse(status_code=200, content={"ok": True, "sample": (sample or '')[:500]})
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


@app.get("/diag/lastpush")
async def diag_lastpush():
    """Return the last push notification attempt recorded by the server (for debugging webhooks)."""
    try:
        return JSONResponse(status_code=200, content={"ok": True, "last_push": _LAST_PUSH.get('last') if isinstance(_LAST_PUSH, dict) else None})
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

