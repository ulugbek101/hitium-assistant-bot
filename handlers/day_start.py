from datetime import datetime, date
from zoneinfo import ZoneInfo
from aiogram import types

from i18n.translate import t
from loader import db
from router import router
from utils.helpers import check_working_day


@router.callback_query(lambda call: call.data.startswith("day_start"))
async def start_working_day(call: types.CallbackQuery, lang: str):
    telegram_id = call.from_user.id
    is_day_started = call.data.split(":")[-1] == "yes"
 
    user = db.get_user(telegram_id=telegram_id)
    day = db.get_day(day_date=date.today())
    is_user_already_checked = (db.get_attendance(user_id=user.get("id"), day_id=day.get("id")) or {}).get("start_time")

    # Skip user check if already checked and remove an unnecessary keyboard to avoid next random click on it
    if is_user_already_checked: 
        await call.message.delete_reply_markup()
        return

    # Skip, if user is checking attendance other day like Sunday
    if not check_working_day():
        return

    # Update is_absent
    db.update_user_attendance(user_id=user.get("id"), is_absent=int(not is_day_started))

    if is_day_started:
        # Update start_time with Asia/Tashkent timezone
        tashkent_time = datetime.now(ZoneInfo("Asia/Tashkent")).time()
        db.update_user_attendance_time(user_id=user.get("id"), field_name="start_time", time=tashkent_time)

    # Send response
    day_start_message = "day_start_success" if is_day_started else "day_start_fail"
    await call.message.answer(text=t(key=day_start_message, lang=lang))
    await call.message.delete_reply_markup()
