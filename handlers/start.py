from aiogram import types
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from enums import languages
from router import router
from states.registration import Registration


@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext, lang: str):
    markup = ReplyKeyboardBuilder()
    for lang in languages.keys():
        markup.button(text=lang)
    markup.adjust(2)

    await message.answer(
        text="Iltimos, tilni tanlang.\n\n"
             "Пожалуйста, выберите язык",
        reply_markup=markup.as_markup(
            one_time_keyboard=True,
            resize_keyboard=True,
        )
    )
    await state.set_state(Registration.lang)
