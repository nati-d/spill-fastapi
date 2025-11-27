from fastapi import APIRouter, HTTPException, Header
from utils.telegram import validate_init_data
from features.nickname.service import generate_suggestions, reserve_nickname

router = APIRouter(prefix="/nickname", tags=["nickname"])

@router.get("/suggestions", response_model=list[str])
async def get_nickname_suggestions():
    return generate_suggestions()

@router.post("/reserve", response_model=bool)
async def reserve_nickname(nickname: str, x_telegram_init_data: str = Header(...)):
    user = validate_init_data(x_telegram_init_data)
    if reserve_nickname(user["id"], nickname):
        return True
    
    raise HTTPException(status_code=409, detail="Already taken")