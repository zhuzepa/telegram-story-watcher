import asyncio

from story_watcher.config import load_settings
from story_watcher.telegram_api import show_pinned_stories


def main() -> None:
    settings = load_settings()
    asyncio.run(show_pinned_stories(settings))


if __name__ == "__main__":
    main()