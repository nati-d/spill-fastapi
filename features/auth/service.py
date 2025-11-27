from database.supabase import supabase
from utils.telegram import validate_init_data
from features.nickname.service import generate_suggestions


def login_or_register(init_data: str):
    user = validate_init_data(init_data)

    response = supabase.table("profiles").upsert(
        {
            "telegram_id": user["id"],
            "telegram_username": user.get("username"),
            "telegram_data": user,
        },
        on_conflict="telegram_id"
    ).execute()

    profile = response.data[0]

    if profile["nickname"]:
        return {"user": profile}
    
    return {"user": profile, "nickname_suggestions": generate_suggestions()}