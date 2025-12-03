from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    profile_photo_url: Optional[str] = None
    language_code: Optional[str] = "en"
    nickname: str
    nickname_set_at: Optional[datetime] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    interests: Optional[list[str]] = None
    photo_urls: Optional[list[str]] = None
    social_links: Optional[dict] = None
    allow_discovery: bool = False
    is_banned: bool = False
    banned_at: Optional[datetime] = None
    banned_reason: Optional[str] = None
    stars_balance: int = 0
    is_premium: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    user: User
    nickname_suggestions: Optional[list[str]] = None