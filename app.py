import asyncio
import logging

from aiogram.types import BotCommand

from loader import dp, bot
from handlers.start import router
from scheduler import start_scheduler


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="tasks", description="Мои задачи"),
        BotCommand(command="info", description="Обо мне"),
    ])
    start_scheduler()
    await dp.start_polling(bot)


if __name__ == "__main__":
    dp.include_router(router=router)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
