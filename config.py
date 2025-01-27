import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

def getenv(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Missing environment variable: {key}")
    return value

DISCORD_API_TOKEN = getenv("DISCORD_API_TOKEN")
HQ_CHANNEL_ID = int(getenv("HQ_CHANNEL_ID") or 0)

DB_URL = getenv("DB_URL")
DB_PORT = getenv("DB_PORT")
DB_DATABASE = getenv("DB_DATABASE")
DB_USER = getenv("DB_USER")
DB_PASS = getenv("DB_PASS")

TORTOISE_ORM: Dict[str, Any] = {
    "connections": {
        "default": f"postgres://{DB_USER}:{DB_PASS}@{DB_URL}:{DB_PORT}/{DB_DATABASE}"
    },
    "apps": {"models": {"models": [], "default_connection": "default"}},
    "use_tz": True,
}