from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from services.OpenRouter import OpenRouterService

app = FastAPI()

# Mount the static folder so you can open /static/index.html in the browser for testing
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root(request: Request):
    # Keep the JSON root for API users, but provide a link to the simple UI
    return {"message": "Welcome to the FastAPI application!", "ui": "/static/index.html"}

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

