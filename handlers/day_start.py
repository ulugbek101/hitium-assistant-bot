from datetime import datetime

from aiogram import types

from i18n.translate import t
from loader import db, dp
from router import router


@router.callback_query(lambda call: call.data.startswith("day_start"))
async def start_working_day(call: types.CallbackQuery, lang: str):
    is_day_started = call.data.split(":")[-1] == "yes"
    telegram_id = call.from_user.id
    user = db.get_user(telegram_id=telegram_id)

    db.update_user_attendance(user_id=user.get("id"), is_absent=int(not is_day_started))
    db.update_user_attendance_time(user_id=user.get("id"), field_name="start_time", time=datetime.now().time())

    day_start_message = "day_start_success" if is_day_started else "day_start_fail"

    await call.message.answer(
        text=t(key=day_start_message, lang=lang)
    )

    await call.message.delete_reply_markup()
