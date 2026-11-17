import asyncio
from getpass import getpass

import qrcode
from telethon.errors import SessionPasswordNeededError

from telethon import TelegramClient, functions, types

from story_watcher.config import Settings


async def authorize_with_qr(client: TelegramClient) -> None:
    await client.connect()

    if await client.is_user_authorized():
        return

    qr_login = await client.qr_login()

    qr = qrcode.QRCode(border=1)
    qr.add_data(qr_login.url)
    qr.make(fit=True)
    qr.print_ascii(invert=True)

    print(
        "Открой Telegram на телефоне: "
        "Настройки → Устройства → Подключить устройство."
    )

    try:
        await qr_login.wait()
    except SessionPasswordNeededError:
        password = getpass("Введите локально пароль 2FA: ")
        await client.sign_in(password=password)
    except asyncio.TimeoutError as error:
        raise RuntimeError(
            "QR-код истёк. Запустите программу ещё раз."
        ) from error


async def show_pinned_stories(settings: Settings) -> None:
    """Выводит безопасную сводку сохранённых историй пользователя."""

    settings.session_path.parent.mkdir(parents=True, exist_ok=True)

    client = TelegramClient(
        str(settings.session_path),
        settings.api_id,
        settings.api_hash,
    )

    await authorize_with_qr(client)
    try:
        user = await client.get_me()

        if user is None or getattr(user, "bot", False):
            raise RuntimeError(
                "Нужно войти через личный аккаунт Telegram, а не через бота."
            )

        result = await client(
            functions.stories.GetPinnedStoriesRequest(
                peer=types.InputPeerSelf(),
                offset_id=0,
                limit=100,
            )
        )

        stories = result.stories
        print(f"Сохранённых историй в профиле: {len(stories)}")

        for story in stories:
            story_id = getattr(story, "id", "?")
            date = getattr(story, "date", None)
            views = getattr(story, "views", None)

            date_text = (
                date.astimezone().strftime("%d.%m.%Y %H:%M")
                if date is not None
                else "неизвестно"
            )
            views_count = getattr(views, "views_count", 0)
            has_viewers = bool(getattr(views, "has_viewers", False))

            print(
                f"История {story_id}: "
                f"дата={date_text}, "
                f"просмотров={views_count}, "
                f"список зрителей={'доступен' if has_viewers else 'не подтверждён'}"
            )
        if not stories:
            return

        latest_story = max(stories, key=lambda item: item.id)

        viewers_result = await client(
            functions.stories.GetStoryViewsListRequest(
                peer=types.InputPeerSelf(),
                id=latest_story.id,
                offset="",
                limit=10,
            )
        )

        print(
            f"\nПроверка истории {latest_story.id}: "
            f"получено {len(viewers_result.views)} записей, "
            f"всего доступно {viewers_result.count}"
        )

    finally:
        await client.disconnect()
