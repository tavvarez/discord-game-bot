import os
from dotenv import load_dotenv

load_dotenv()
class Settings:
    DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL")
    BASE_URL: str = os.getenv("BASE_URL")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()