from fastapi import HTTPException, UploadFile
from database.supabase import supabase
from features.nickname.service import generate_nickname
from utils.telegram import validate_init_data, upload_image_to_telegram
from features.auth.schemas import User
import logging

logger = logging.getLogger(__name__)


def _get_user_dict(telegram_user) -> dict:
    """Convert Telegram user object to dictionary."""
    if hasattr(telegram_user, 'model_dump'):
        return telegram_user.model_dump()
    elif hasattr(telegram_user, 'dict'):
        return telegram_user.dict()

    fields = ["id", "username", "first_name", "last_name", "language_code"]
    return {field: getattr(telegram_user, field, None) for field in fields}

def get_user(user_id: int):
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None
    
def login_or_register(init_data: str):
    telegram_user = validate_init_data(init_data)
    user_dict = _get_user_dict(telegram_user)

    existing_user_data = get_user(user_dict.get("id"))
    if existing_user_data:
        return {"user": User(**existing_user_data)}
    else:
        new_user = {
            "id":user_dict.get("id"),
            "first_name":user_dict.get("first_name"),
            "last_name":user_dict.get("last_name"),
            "language_code":user_dict.get("language_code"),
            "username":user_dict.get("username"),
            "nickname":generate_nickname().nickname,
        }
        new_user = {k: v for k, v in new_user.items() if v is not None}
        insert_response = supabase.table("users").insert(new_user).execute()
        if insert_response.data:
            return {"user": User(**insert_response.data[0])}
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")

def update_user(user_id: int, user_data: dict):
    response = supabase.table("users").update(user_data).eq("id", user_id).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None


async def process_photo_uploads(photos: list[UploadFile], user_id: int) -> list[str]:
    """
    Process uploaded photos, upload them to Telegram, and return the URLs.
    
    Args:
        photos: List of uploaded photo files
        user_id: User ID for the caption
        
    Returns:
        List of photo URLs from Telegram
    """
    photo_urls = []
    
    for photo in photos:
        try:
            # Read file bytes
            file_bytes = await photo.read()
            
            # Generate file name if not provided
            file_name = photo.filename or f"photo_{user_id}_{len(photo_urls)}.jpg"
            
            # Create caption
            caption = f"User {user_id} profile photo"
            
            # Upload to Telegram
            photo_url = upload_image_to_telegram(file_bytes, file_name, caption)
            photo_urls.append(photo_url)
            
        except Exception as e:
            logger.error(f"Error uploading photo {photo.filename}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload photo {photo.filename}: {str(e)}"
            )
    
    return photo_urls