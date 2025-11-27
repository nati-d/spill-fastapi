from fastapi import APIRouter, HTTPException, Form, Request
from features.auth.schemas import AuthResponse
from features.auth.service import login_or_register
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

class TelegramAuthRequest(BaseModel):
    init_data: str

@router.post("/telegram", response_model=AuthResponse)
async def telegram_auth(
    request: Request,
    init_data: str = Form(None)
):
    """
    Authenticate with Telegram init data.
    Accepts either form data (init_data) or JSON body ({"init_data": "..."}).
    """
    # Try to get init_data from form first, then from JSON body
    if not init_data:
        try:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                body = await request.json()
                init_data = body.get("init_data")
        except Exception as e:
            logger.warning(f"Failed to parse JSON body: {e}")
    
    if not init_data:
        logger.error("init_data is missing from request")
        raise HTTPException(
            status_code=400, 
            detail="init_data is required. Send as form field 'init_data' or JSON body {'init_data': '...'}"
        )
    
    try:
        return login_or_register(init_data)
    except ValueError as e:
        error_msg = str(e)
        logger.error(f"Telegram auth validation error: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = f"Unexpected error during authentication: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")