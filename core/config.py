from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    TELEGRAM_BOT_TOKEN: str


    class Config:
        env_file = ".env"

settings = Settings()