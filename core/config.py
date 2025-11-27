from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    TELEGRAM_BOT_TOKEN: str
    port: int = 8000
    dev_mode: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env file

settings = Settings()