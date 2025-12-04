import logging
from fastapi import APIRouter, HTTPException, Header, Body, Form, File, UploadFile
from features.auth.schemas import AuthResponse, User, UserUpdate
from features.auth.service import get_user, login_or_register, update_user as update_user_service, process_photo_uploads
from utils.telegram import validate_init_data
from typing import Annotated, Optional, List

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
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    interests: Optional[str] = Form(None),  # JSON string, will be parsed
    social_links: Optional[str] = Form(None),  # JSON string, will be parsed
    photos: Optional[List[UploadFile]] = File(None)
):
    """
    Update the current user's information.
    Photos can be uploaded as files, which will be uploaded to Telegram and URLs stored.
    """
    if not x_telegram_init_data:
        raise HTTPException(status_code=400, detail="X-Telegram-InitData header is required")
    
    try:
        telegram_user = validate_init_data(x_telegram_init_data)
        
        # Build update data
        user_data = {}
        if first_name is not None:
            user_data["first_name"] = first_name
        if last_name is not None:
            user_data["last_name"] = last_name
        if age is not None:
            user_data["age"] = age
        if gender is not None:
            user_data["gender"] = gender
        if bio is not None:
            user_data["bio"] = bio
        if interests is not None:
            import json
            try:
                user_data["interests"] = json.loads(interests)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid interests format. Must be valid JSON array.")
        if social_links is not None:
            import json
            try:
                user_data["social_links"] = json.loads(social_links)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid social_links format. Must be valid JSON object.")
        
        # Process photo uploads if provided
        if photos:
            uploaded_photo_urls = await process_photo_uploads(photos, telegram_user.id)
            # If photo_urls already exists, append; otherwise create new list
            if "photo_urls" in user_data:
                existing_urls = user_data.get("photo_urls", []) or []
                user_data["photo_urls"] = existing_urls + uploaded_photo_urls
            else:
                user_data["photo_urls"] = uploaded_photo_urls
        
        if not user_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        updated_user = update_user_service(telegram_user.id, user_data)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return User(**updated_user)
    except ValueError as e:
        logger.error(f"Error authenticating with Telegram: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")