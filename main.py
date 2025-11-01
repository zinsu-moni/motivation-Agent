"""
Motivation Agent - A2A Protocol Implementation
Built with FastAPI and OpenRouter AI
"""
import os
import asyncio
import logging
from typing import Optional

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from models import (
    A2ARequest,
    A2AResponse,
    A2AResponseResult,
    A2AResponseMessage,
    A2AResponsePart,
)
from services import MotivationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Motivation Agent", version="1.0.0")

# Initialize service
motivation_service = MotivationService(api_key=os.getenv("OPENAI_API_KEY"))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "motivation-agent"}


@app.post("/a2a/motivation")
async def handle_a2a_motivation(request: Request):
    """
    Main A2A endpoint for handling motivation requests.
    
    Expects JSON-RPC 2.0 format with Telex A2A protocol.
    Returns immediately with 200 OK, then sends response via webhook.
    """
    try:
        # Parse request
        body = await request.json()
        logger.info(f"[REQUEST] Raw body keys: {body.keys()}")
        
        a2a_request = A2ARequest(**body)
        
        # Log incoming request
        user_message = ""
        for part in a2a_request.params.message.parts:
            if part.kind == "text" and part.text:
                user_message += part.text + " "
        
        logger.info(f"[REQUEST] Received A2A request (id={a2a_request.id})")
        logger.info(f"[REQUEST] User message: {user_message[:100]}...")
        logger.info(f"[REQUEST] Method: {a2a_request.method}")
        
        # Check if webhook is configured (async mode)
        webhook_config = a2a_request.params.configuration.pushNotificationConfig if a2a_request.params.configuration else None
        is_async = not a2a_request.params.configuration.blocking if a2a_request.params.configuration else False
        
        logger.info(f"[REQUEST] Webhook config present: {webhook_config is not None}")
        logger.info(f"[REQUEST] Async mode: {is_async}")
        
        if webhook_config:
            logger.info(f"[REQUEST] Webhook URL: {webhook_config.url}")
            logger.info(f"[REQUEST] Webhook token present: {webhook_config.token is not None}")
        
        if is_async and webhook_config:
            logger.info(" Async mode: Will send response via webhook")
            
            # Return immediately
            immediate_response = {
                "jsonrpc": "2.0",
                "id": a2a_request.id,
                "result": {
                    "message": {
                        "kind": "message",
                        "role": "assistant",
                        "parts": [
                            {"kind": "text", "text": "Processing your request..."}
                        ]
                    }
                }
            }
            
            # Schedule background webhook delivery
            asyncio.create_task(
                deliver_motivation_via_webhook(
                    user_message.strip(),
                    a2a_request.id,
                    webhook_config.url,
                    webhook_config.token,
                )
            )
            
            return JSONResponse(status_code=200, content=immediate_response)
        
        else:
            logger.info(" Blocking mode: Will send response directly")
            
            # Generate motivation synchronously
            motivation = await motivation_service.generate_motivation(user_message.strip())
            
            # Build A2A response
            response = A2AResponse(
                id=a2a_request.id,
                result=A2AResponseResult(
                    message=A2AResponseMessage(
                        parts=[A2AResponsePart(kind="text", text=motivation)]
                    )
                )
            )
            
            logger.info(f" Generated response (id={a2a_request.id})")
            return JSONResponse(status_code=200, content=response.model_dump())
    
    except Exception as e:
        logger.error(f" Error handling A2A request: {e}", exc_info=True)
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
        )


async def deliver_motivation_via_webhook(
    user_message: str,
    request_id: str,
    webhook_url: str,
    webhook_token: Optional[str] = None,
):
    """
    Generate motivation and deliver via webhook callback.
    
    This runs in the background and doesn't block the HTTP response.
    """
    try:
        logger.info(f"[WEBHOOK] Starting background task for request {request_id}")
        logger.info(f"[WEBHOOK] Webhook URL: {webhook_url}")
        logger.info(f"[WEBHOOK] Token present: {webhook_token is not None}")
        
        # Generate motivation
        logger.info(f"[WEBHOOK] Generating motivation from message: {user_message[:50]}...")
        try:
            motivation = await motivation_service.generate_motivation(user_message)
            logger.info(f"[WEBHOOK] Generated motivation: {motivation}")
        except Exception as gen_error:
            logger.error(f"[WEBHOOK] ERROR generating motivation: {type(gen_error).__name__}: {gen_error}", exc_info=True)
            motivation = "You've got this! Keep pushing forward and believe in yourself."
            logger.info(f"[WEBHOOK] Using fallback motivation")
        
        # Build A2A response
        result = {
            "message": {
                "kind": "message",
                "role": "assistant",
                "parts": [
                    {"kind": "text", "text": motivation}
                ],
                "messageId": f"response-{request_id}"
            }
        }
        
        webhook_body = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        
        logger.info(f"[WEBHOOK] Built request body: {str(webhook_body)[:200]}...")
        
        # Send webhook with authentication
        headers = {"Content-Type": "application/json"}
        if webhook_token:
            headers["Authorization"] = f"Bearer {webhook_token}"
            logger.info(f"[WEBHOOK] Using Bearer token for authentication")
        else:
            logger.warning(f"[WEBHOOK] No token provided for webhook!")
        
        logger.info(f"[WEBHOOK] Sending POST to: {webhook_url}")
        logger.info(f"[WEBHOOK] Headers: {list(headers.keys())}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                logger.info(f"[WEBHOOK] Making HTTP POST request...")
                resp = await client.post(webhook_url, json=webhook_body, headers=headers)
                
                logger.info(f"[WEBHOOK] Response status: {resp.status_code}")
                logger.info(f"[WEBHOOK] Response headers: {dict(resp.headers)}")
                logger.info(f"[WEBHOOK] Response body: {resp.text[:500]}")
                
                if resp.status_code == 200:
                    logger.info(f"[WEBHOOK] SUCCESS - Response delivered to Telex!")
                else:
                    logger.warning(
                        f"[WEBHOOK] FAILED - Status {resp.status_code}: {resp.text[:200]}"
                    )
            except httpx.TimeoutException as te:
                logger.error(f"[WEBHOOK] TIMEOUT after 10s: {te}")
            except Exception as post_error:
                logger.error(f"[WEBHOOK] POST ERROR: {type(post_error).__name__}: {post_error}", exc_info=True)
    
    except asyncio.TimeoutError:
        logger.error("[WEBHOOK] Background task timed out")
    except Exception as e:
        logger.error(f"[WEBHOOK] TOP-LEVEL ERROR: {type(e).__name__}: {e}", exc_info=True)


@app.get("/workflow")
async def get_workflow():
    """Return workflow metadata for Telex integration."""
    return {
        "active": True,
        "id": "motivation_agent_01",
        "name": "motivation_agent",
        "category": "motivation",
        "description": "A compassionate and energetic motivational coach that provides encouragement without asking clarifying questions",
        "nodes": [
            {
                "id": "motivation_handler",
                "type": "a2a/http-endpoint",
                "url": "/a2a/motivation",
                "authentication": {
                    "header": "X-API-KEY",
                    "default_env": "OPENAI_API_KEY"
                },
                "parameters": {
                    "auto_respond": True,
                    "respond_immediately": True,
                    "clarify_if_missing": False
                }
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
