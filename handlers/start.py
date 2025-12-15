from aiogram import types
from aiogram.filters.command import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from router import router
from handlers.registration import register_user


@router.message(CommandStart())
async def start(message: types.Message):
    fullname = message.from_user.full_name

    markup = ReplyKeyboardBuilder()
    markup.button(text="Ro'yxatdan o'tish")

    await message.answer(
        text=f"Assalomu alaykum, {fullname}, davom etish uchun, iltimos, ro'yxatdan o'ting",
        reply_markup=markup.as_markup(
            one_time_keyboard=True,
            resize_keyboard=True
        ),
    )

    await register_user(telegram_id=message.from_user.id)
