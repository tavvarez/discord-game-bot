import os
from dotenv import load_dotenv

load_dotenv()
class Settings:
    # DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL")
    DISCORD_WEBHOOK_URL_ONLINE: str = os.getenv("DISCORD_WEBHOOK_URL_ONLINE")
    DISCORD_WEBHOOK_URL_DEATH: str = os.getenv("DISCORD_WEBHOOK_URL_DEATH")
    BASE_URL: str = os.getenv("BASE_URL")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()