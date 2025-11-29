import logging
from fastapi import APIRouter, HTTPException, Header
from features.auth.schemas import AuthResponse
from features.auth.service import login_or_register
from typing import Annotated

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/telegram", response_model=AuthResponse)
async def telegram_auth(
    x_telegram_init_data: Annotated[str | None, Header(alias="X-Telegram-InitData")] = None
):
    """
    Authenticate with Telegram init data from X-Telegram-InitData header.
    """
    if not x_telegram_init_data:
        raise HTTPException(
            status_code=400,
            detail="X-Telegram-InitData header is required"
        )
    
    try:
        return login_or_register(x_telegram_init_data)
    except ValueError as e:
        logger.error(f"Error authenticating with Telegram: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error authenticating with Telegram: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")