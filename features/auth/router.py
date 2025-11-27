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
    
    IMPORTANT: The init_data should be the RAW query string from Telegram Web App,
    not URL-decoded. It should look like: "user=%7B%22id%22%3A123...&hash=..."
    """
    # Try to get init_data from form first, then from JSON body
    if not init_data:
        try:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                body = await request.json()
                init_data = body.get("init_data")
            elif "application/x-www-form-urlencoded" in content_type:
                # Try to get raw body for form data
                body_bytes = await request.body()
                body_str = body_bytes.decode('utf-8')
                # Extract init_data from raw form string
                for part in body_str.split('&'):
                    if part.startswith('init_data='):
                        init_data = part.split('=', 1)[1]
                        break
        except Exception as e:
            logger.warning(f"Failed to parse request body: {e}")
    
    if not init_data:
        logger.error("init_data is missing from request")
        raise HTTPException(
            status_code=400, 
            detail="init_data is required. Send the RAW query string from Telegram Web App as form field 'init_data' or JSON body {'init_data': '...'}"
        )
    
    # Log first 100 chars for debugging (don't log full data for security)
    logger.debug(f"Received init_data (first 100 chars): {init_data[:100]}...")
    
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