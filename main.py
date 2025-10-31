from fastapi import FastAPI, Request, Response
from services.OpenRouter import OpenRouterService

app = FastAPI()

@app.get("/")
async def read_root(request: Request):
    return {"message": "Welcome to the FastAPI application!"}

@app.get("/motivation")
async def get_motivation(request: Request):
    api_key = request.headers.get("X-API-KEY")
    if not api_key:
        return Response(content="API key missing", status_code=401)

    openrouter_service = OpenRouterService(api_key=api_key)
    quote = await openrouter_service.generate_motivation()
    return {"motivation": quote}

