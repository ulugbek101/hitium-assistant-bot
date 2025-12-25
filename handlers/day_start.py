from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from i18n.translate import t
from loader import db, dp
from router import router


@router.callback_query(lambda call: "day_start:yes")
@router.callback_query(lambda call: "day_start:no")
async def start_working_day(call: types.CallbackQuery, lang: str):
    is_day_started = call.data.split(":")[-1] == "yes"
    telegram_id = call.from_user.id
    user = db.get_user(telegram_id=telegram_id)

    db.update_user_attendance(user_id=user.get("id"), is_absent=int(not is_day_started))

    day_start_message = "day_start_success" if is_day_started else "day_start_fail"

    await call.message.answer(
        text=t(key=day_start_message, lang=lang)
    )

    await call.message.delete_reply_markup()
