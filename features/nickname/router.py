from fastapi import APIRouter, HTTPException, Header, Body
from utils.telegram import validate_init_data
from features.nickname.service import generate_suggestions, reserve_nickname
from pydantic import BaseModel

router = APIRouter(prefix="/nickname", tags=["nickname"])

class ReserveNicknameRequest(BaseModel):
    nickname: str

@router.get("/suggestions", response_model=list[str])
async def get_nickname_suggestions():
    return generate_suggestions()

@router.post("/reserve", response_model=bool)
async def reserve_nickname(
    request_body: ReserveNicknameRequest = Body(...),
    x_telegram_init_data: str = Header(..., alias="X-Telegram-InitData")
):
    """
    Reserve a nickname for the authenticated user.
    Accepts nickname in JSON body and init_data in header.
    """
    user = validate_init_data(x_telegram_init_data)
    if reserve_nickname(user["id"], request_body.nickname):
        return True
    
    raise HTTPException(status_code=409, detail="Already taken")