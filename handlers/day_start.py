from datetime import datetime
from zoneinfo import ZoneInfo
from aiogram import types

from i18n.translate import t
from loader import db
from router import router

@router.callback_query(lambda call: call.data.startswith("day_start"))
async def start_working_day(call: types.CallbackQuery, lang: str):
    is_day_started = call.data.split(":")[-1] == "yes"
    telegram_id = call.from_user.id
    user = db.get_user(telegram_id=telegram_id)

    # Update is_absent
    db.update_user_attendance(user_id=user.get("id"), is_absent=int(not is_day_started))

    # Update start_time with Asia/Tashkent timezone
    tashkent_time = datetime.now(ZoneInfo("Asia/Tashkent")).time()
    db.update_user_attendance_time(user_id=user.get("id"), field_name="start_time", time=tashkent_time)

    # Send response
    day_start_message = "day_start_success" if is_day_started else "day_start_fail"
    await call.message.answer(text=t(key=day_start_message, lang=lang))
    await call.message.delete_reply_markup()
