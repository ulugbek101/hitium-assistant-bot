from datetime import date
from datetime import time
from loader import db

from aiogram.utils.keyboard import InlineKeyboardBuilder

from i18n.translate import t
from loader import bot, db, ADMINS
from utils.helpers import check_working_day

CUTOFF_TIME = time(21, 0)


async def day_start():
    """
    Task to send a message to all users a question whether a worker started his/her working day or not
    """

    users = db.get_users()

    successes = []
    fails = []
    total = len(users)

    for user in users:
        lang = user.get("lang")

        markup = InlineKeyboardBuilder()
        markup.button(text=t(key="day_start_no", lang=lang), callback_data="day_start:no")
        markup.button(text=t(key="day_start_yes", lang=lang), callback_data="day_start:yes")
        markup.adjust(1)

        try:
            await bot.send_message(
                chat_id=user.get("telegram_id"),
                text=t(key="day_start", lang=lang),
                reply_markup=markup.as_markup(),
            )
            successes.append({"first_name": user.get("first_name"), "last_name": user.get("last_name")})
        except:
            fails.append({"first_name": user.get("first_name"), "last_name": user.get("last_name")})

    failed_users = ", ".join([f"{fail.get('first_name')} {fail.get('last_name')}".title() for fail in fails])
    msg = ("Сообщение о начале рабочего дня отправлено\n\n"
           f"Всего пользователей: {total}\n"
           f"Всего отправлено: {len(successes)}\n"
           f"Не отправлено: {len(fails)}\n\n")

    if len(fails) > 0:
        msg += f"Не удалось отправить пользователям: {failed_users}"

    for admin in ADMINS:
        try:
            await bot.send_message(
                chat_id=admin,
                text=msg,
            )
        except:
            pass


async def day_end():
    """
    Task to send a message to all users a question whether a worker finished his/her working day or not
    """
    successes = []
    fails = []
    total = len(users)

    users = db.get_users()

    for user in users:
        # Chech if user started working day
        user_id = db.get_user(telegram_id=user.get("telegram_id")).get("id")
        day_id = db.get_day(date=date.today()).get("id")
        is_user_worked_today = db.get_attendance(user_id=user_id, day_id=day_id).get("start_time")
        is_user_finished_already = db.get_attendance(user_id=user_id, day_id=day_id).get("end_time")

        if not is_user_worked_today or not is_user_finished_already:
            fails.append({"first_name": user.get("first_name"), "last_name": user.get("last_name")})
            continue

        lang = user.get("lang")

        markup = InlineKeyboardBuilder()
        markup.button(text=t(key="day_end_no", lang=lang), callback_data="day_end:no")
        markup.button(text=t(key="day_end_yes", lang=lang), callback_data="day_end:yes")
        markup.adjust(1)

        try:
            await bot.send_message(
                chat_id=user.get("telegram_id"),
                text=t(key="day_end", lang=lang),
                reply_markup=markup.as_markup(),
            )
            successes.append({"first_name": user.get("first_name"), "last_name": user.get("last_name")})
        except:
            fails.append({"first_name": user.get("first_name"), "last_name": user.get("last_name")})
            pass

    failed_users = ", ".join([f"{fail.get('first_name')} {fail.get('last_name')}".title() for fail in fails])
    msg = ("Сообщение о завершении рабочего дня отправлено\n\n"
           f"Всего пользователей: {total}\n"
           f"Всего отправлено: {len(successes)}\n"
           f"Не отправлено: {len(fails)}\n\n")

    if len(fails) > 0:
        msg += f"Не удалось отправить пользователям: {failed_users}"

    for admin in ADMINS:
        try:
            await bot.send_message(
                chat_id=admin,
                text=msg,
            )
        except:
            pass


def create_working_day():
    """
    Task to create a working day to then attach to it workers attendance
    """

    # Stop task execution if today is not a working day
    is_working_day = check_working_day()
    if not is_working_day:
        return

    today = date.today()

    day = db.get_day(today)
    if not day:
        db.create_day(today)


def create_attendance_for_everyday():
    """
    Task to create attendance for all users as abcent initially to then update it one-by-one to not is absent
    """

    # Stop task execution if today is not a working day
    if not check_working_day():
        return

    today = date.today()
    day = db.get_day(today)
    if not day:
        # Create a day if day was not created
        db.create_day(today)
        day = db.get_day(today)

    users = db.get_users()

    for user in users:
        # Check if attendance already exists to avoid duplicates
        existing = db.get_attendance(user_id=user.get("id"), day_id=day.get("id"))
        if not existing:
            db.create_attendance_for_user(user_id=user.get("id"), day_id=day.get("id"))


def auto_close_all_open_days():
    """
    Closes attendance for all users who did not end the day manually.
    Runs every day at 21:00 Asia/Tashkent.
    """
    users = db.get_users_with_open_attendance()

    for user in users:
        db.update_user_attendance(
            user_id=user["id"],
            is_absent=1
        )
        db.update_user_attendance_time(
            user_id=user["id"],
            field_name="end_time",
            time=CUTOFF_TIME
        )
