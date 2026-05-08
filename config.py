import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    group_id: int
    db_path: str


def load_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    group_id_raw = os.getenv("GROUP_ID", "").strip()
    db_path = os.getenv("DB_PATH", "bot.sqlite3").strip()

    if not bot_token:
        raise RuntimeError("BOT_TOKEN is missing in environment/.env")
    if not group_id_raw:
        raise RuntimeError("GROUP_ID is missing in environment/.env")

    try:
        group_id = int(group_id_raw)
    except ValueError as e:
        raise RuntimeError("GROUP_ID must be an integer (e.g. -1001234567890)") from e

    return Settings(bot_token=bot_token, group_id=group_id, db_path=db_path)


settings = load_settings()

