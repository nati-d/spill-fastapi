from database.supabase import supabase
from utils.telegram import validate_init_data


def login_or_register(init_data: str):
    user = validate_init_data(init_data)

    # Convert user object to dict (handles Pydantic models)
    if hasattr(user, 'model_dump'):
        user_dict = user.model_dump()
    elif hasattr(user, 'dict'):
        user_dict = user.dict()
    else:
        # Fallback: access as attributes
        user_dict = {
            "id": getattr(user, "id", None),
            "username": getattr(user, "username", None),
        }

    response = supabase.table("profiles").upsert(
        {
            "telegram_id": user_dict.get("id"),
            "telegram_username": user_dict.get("username"),
            "telegram_data": user_dict,
        },
        on_conflict="telegram_id"
    ).execute()

    profile = response.data[0]

    print(profile)
    return {"user": profile}