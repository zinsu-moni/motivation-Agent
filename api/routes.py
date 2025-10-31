from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from schemas.telex import *
from schemas.telex import SendMessageParams
from services.OpenRouter import OpenAIService
from services.users import UserService
from dotenv import load_dotenv
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter()
env = load_dotenv()

openai_service = OpenAIService()
user_service = UserService()


@router.post("/telex", response_model=TelexResponse)
async def handle_telex(request: TelexRequest, db: AsyncSession = Depends(get_db)):
    """Handle JSON-RPC 2.0 requests"""
    start_time = time.time()
    
    try:
        if request.method == "message/send":
            result = await handle_send_message(request.params, db, start_time)
        elif request.method == "user/onboard":
            result = await handle_onboard_user(request.params, db)
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": -32601,
                    "message": "Method not found",
                    "data": f"Unknown method: {request.method}"
                }
            )

        return TelexResponse(
            result=result,
            id=request.id
        )
    
    except HTTPException as e:
        return TelexResponse(
            error={
                "code": e.status_code,
                "message": str(e.detail),
                "data": None
            },
            id=request.id
        )
    except Exception as e:
        logger.error(f"Error handling JSON-RPC request: {e}")
        return TelexResponse(
            error={
                "code": -32603,
                "message": "Internal error",
                "data": str(e)
            },
            id=request.id
        )

async def handle_send_message(params: dict, db: AsyncSession, start_time: float) -> dict:
    """Handle message/send method"""
    try:
        # Parse parameters
        send_params = SendMessageParams(**params)
        user_message = send_params.message.parts[0].content
        user_id = send_params.user_id
        
        ai_response = await openai_service.generate_motivation(user_message, user_id, db)

        response_time_ms = int((time.time() - start_time) * 1000)
        await user_service.log_motivation_interaction(
            db, user_id, user_message, ai_response, "api", response_time_ms
        )
        
        result = SendMessageResult(
            response=ai_response,
            agent=Agent(
                name=env['AGENT_NAME'],
                title=env['AGENT_TITLE'],
                version=env['AGENT_VERSION']
            )
        )
        
        return result.dict()
    
    except Exception as e:
        logger.error(f"Error in handle_send_message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
