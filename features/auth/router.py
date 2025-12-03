import logging
from fastapi import APIRouter, HTTPException, Header, Body
from features.auth.schemas import AuthResponse, User, UserUpdate
from features.auth.service import get_user, login_or_register, update_user as update_user_service
from utils.telegram import validate_init_data
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

@router.patch("/me", response_model=User)
async def update_user(
    x_telegram_init_data: Annotated[str | None, Header(alias="X-Telegram-InitData")] = None,
    user_data: UserUpdate = Body(...)
):
    """
    Update the current user's information.
    """
    if not x_telegram_init_data:
        raise HTTPException(status_code=400, detail="X-Telegram-InitData header is required")
    
    try:
        telegram_user = validate_init_data(x_telegram_init_data)
        updated_user = update_user_service(telegram_user.id, user_data.model_dump(exclude_unset=True))
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return User(**updated_user)
    except ValueError as e:
        logger.error(f"Error authenticating with Telegram: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")