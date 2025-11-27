from pydantic import BaseModel

class AuthResponse(BaseModel):
    user: dict
    nickname_suggestions: list[str] | None = None