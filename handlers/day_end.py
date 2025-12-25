from datetime import timedelta, datetime

from aiogram import types

from i18n.translate import t
from loader import db
from router import router
from scheduler import scheduler
from scheduled_notifications import day_end


@router.callback_query(lambda call: call.data.startswith("day_end"))
async def end_working_day(call: types.CallbackQuery, lang: str):

    is_day_ended = call.data.split(":")[-1] == "yes"
    telegram_id = call.from_user.id
    user = db.get_user(telegram_id=telegram_id)

    db.update_user_attendance(user_id=user.get("id"), is_absent=int(not is_day_ended))

    if is_day_ended:
        await call.message.answer(
            text=t(key="day_end_success", lang=lang)
        )
        db.update_user_attendance_time(user_id=user.get("id"), field_name="end_time", time=datetime.now().time())

    else:
        await call.message.answer(
            text=t(key="day_end_fail", lang=lang)
        )
        run_time = datetime.now() + timedelta(minutes=60)
        scheduler.add_job(day_end, 'date', run_date=run_time)

    await call.message.delete_reply_markup()
