import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


class ConfigError(ValueError):
    """Ошибка в настройках приложения."""


@dataclass(frozen=True)
class Settings:
    api_id: int
    api_hash: str = field(repr=False)
    bot_token: str | None = field(repr=False)
    bot_chat_id: int | None
    session_path: Path
    database_path: Path
    poll_interval_seconds: int


def load_settings(require_bot: bool = False) -> Settings:
    """Загрузить и проверить настройки из локального файла .env."""
    load_dotenv()

    raw_api_id = os.getenv("TELEGRAM_API_ID", "").strip()
    api_hash = os.getenv("TELEGRAM_API_HASH", "").strip()
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip() or None
    raw_bot_chat_id = os.getenv("TELEGRAM_BOT_CHAT_ID", "").strip()

    if not raw_api_id:
        raise ConfigError("В .env не указан TELEGRAM_API_ID")

    try:
        api_id = int(raw_api_id)
    except ValueError as error:
        raise ConfigError("TELEGRAM_API_ID должен быть целым числом") from error

    if api_id <= 0:
        raise ConfigError("TELEGRAM_API_ID должен быть положительным числом")

    if not api_hash:
        raise ConfigError("В .env не указан TELEGRAM_API_HASH")

    if require_bot and not bot_token:
        raise ConfigError("В .env не указан TELEGRAM_BOT_TOKEN")

    bot_chat_id: int | None = None
    if raw_bot_chat_id:
        try:
            bot_chat_id = int(raw_bot_chat_id)
        except ValueError as error:
            raise ConfigError(
                "TELEGRAM_BOT_CHAT_ID должен быть целым числом"
            ) from error

    raw_interval = os.getenv("POLL_INTERVAL_SECONDS", "420").strip()

    try:
        poll_interval_seconds = int(raw_interval)
    except ValueError as error:
        raise ConfigError(
            "POLL_INTERVAL_SECONDS должен быть целым числом"
        ) from error

    if not 300 <= poll_interval_seconds <= 600:
        raise ConfigError(
            "Интервал опроса должен находиться между 300 и 600 секундами"
        )

    return Settings(
        api_id=api_id,
        api_hash=api_hash,
        bot_token=bot_token,
        bot_chat_id=bot_chat_id,
        session_path=Path(
            os.getenv("TELEGRAM_SESSION", "data/user")
        ),
        database_path=Path(
            os.getenv("DATABASE_PATH", "data/story_watcher.sqlite3")
        ),
        poll_interval_seconds=poll_interval_seconds,
    )