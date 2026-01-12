import os

import asyncio
import logging

from aiogram.types import BotCommand

from loader import dp, bot
from handlers.start import router
from scheduler import start_scheduler
from config import MEDIA_ROOT, ADMINS

async def notify_admins():
    for admin in ADMINS:
        await bot.send_message(
            chat_id=admin,
            text="Бот запущен/перезапущен c обновлениями!",
        )


def ensure_media_dirs():
    """
    Create media folders if they don't exist.
    Works even if one exists and the other doesn't.
    """
    os.makedirs(MEDIA_ROOT, exist_ok=True)


async def main():
    ensure_media_dirs()

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="tasks", description="Мои задачи"),
        BotCommand(command="finish_day", description="Уйти пораньше"),
        BotCommand(command="info", description="Обо мне"),
    ])
    start_scheduler()
    await notify_admins()
    await dp.start_polling(bot)


if __name__ == "__main__":
    dp.include_router(router=router)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
