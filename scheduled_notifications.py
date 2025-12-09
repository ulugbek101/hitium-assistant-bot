from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message

from loader import bot, db


async def day_start():
    users = db.get_users()

    markup = InlineKeyboardBuilder()
    markup.button(text="Да, уже начинаю", callback_data="day_start:yes")
    markup.adjust(1)

    for user in users:
        await bot.send_message(
            chat_id=user.get("telegram_id"),
            text="Здравствуйте, как вы ?\n"
                 "Вы уже начали рабочий день ?",
            reply_markup=markup.as_markup(),
        )
