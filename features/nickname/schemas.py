from pydantic import BaseModel


class Nickname(BaseModel):
    nickname: str

    class Config:
        from_attributes = True

class NicknameResponse(BaseModel):
    nickname: str