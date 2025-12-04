from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


load_dotenv()

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    TELEGRAM_BOT_TOKEN: str
    port: int = int(os.getenv("PORT", "8000"))  # Render provides PORT env var
    dev_mode: bool = False
    TELEGRAM_CHANNEL_ID: str

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env file

settings = Settings()