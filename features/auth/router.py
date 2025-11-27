from fastapi import APIRouter, HTTPException, Form
from features.auth.schemas import AuthResponse
from features.auth.service import login_or_register


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/telegram", response_model=AuthResponse)
async def telegram_auth(init_data: str = Form(...)):
    try:
        return login_or_register(init_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))