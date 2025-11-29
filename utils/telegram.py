from init_data_py import InitData
from core.config import settings

def validate_init_data(init_data: str):
    parsed_init_data = InitData.parse(init_data)

    if not parsed_init_data.validate(bot_token=settings.TELEGRAM_BOT_TOKEN, lifetime=86400):
        raise ValueError("Invalid init data")

    return parsed_init_data.user