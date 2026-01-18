from functools import partial
from datetime import timedelta
from aiogram import types

from utils.time_utils import now_tashkent, CUTOFF_TIME
from scheduler import scheduler
from scheduled_notifications import day_end

from i18n.translate import t
from loader import db
from router import router


@router.callback_query(lambda call: call.data.startswith("day_end"))
async def end_working_day(call: types.CallbackQuery, lang: str):
    is_day_ended = call.data.split(":")[-1] == "yes"
    telegram_id = call.from_user.id
    user = db.get_user(telegram_id=telegram_id)

    now = now_tashkent()

    # Skip, if worker is finishing day next day or after CUT OFF (21:00)
    is_user_already_finished = (db.get_attendance(user_id=user.get("id"), day_id=now.date()) or {}).get("end_time")
    if not is_user_already_finished:
        await call.message.delete_reply_markup()
        return

    if is_day_ended:
        db.update_user_attendance(
            user_id=user["id"],
            is_absent=0
        )
        db.update_user_attendance_time(
            user_id=user["id"],
            field_name="end_time",
            time=now.time()
            )

        await call.message.delete_reply_markup()
        await call.message.answer(
            text=t(key="day_end_success", lang=lang)
        )

    else:
        await call.message.answer(
            text=t(key="day_end_fail", lang=lang)
        )

        run_time = now + timedelta(minutes=60)

        if run_time.time() < CUTOFF_TIME:
            scheduler.add_job(
                day_end,
                trigger="date",
                run_date=run_time,
                id=f"day_end_remainder_for_user_with_id_{user.get('id')}",
                replace_existing=True,
                kwargs={
                    "again": True,
                    "chat_id": telegram_id,
                    "lang": lang,
                },
            )

    await call.message.delete_reply_markup()
