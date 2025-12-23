from datetime import date

from aiogram.utils.keyboard import InlineKeyboardBuilder

from i18n.translate import t
from loader import bot, db
from utils.helpers import check_working_day


async def day_start():
    """
    Task to send a message to all users a question whether a worker started his/her working day or not
    """

    users = db.get_users()

    for user in users:
        lang = user.get("lang")

        markup = InlineKeyboardBuilder()
        markup.button(text=t(key="day_start_no", lang=lang), callback_data="day_start:no")
        markup.button(text=t(key="day_start_yes", lang=lang), callback_data="day_start:yes")
        markup.adjust(1)

        await bot.send_message(
            chat_id=user.get("telegram_id"),
            text=t(key="day_start", lang=lang),
            reply_markup=markup.as_markup(),
        )


async def day_end():
    """
    Task to send a message to all users a question whether a worker finished his/her working day or not
    """

    users = db.get_user()

    for user in users:
        lang = user.get("lang")

        markup = InlineKeyboardBuilder()
        markup.button(text=t(key="day_end_no", lang=lang), callback_data="day_end:no")
        markup.button(text=t(key="day_end_yes", lang=lang), callback_data="day_end:yes")
        markup.adjust(1)

        await bot.send_message(
            chat_id=user.get("telegram_id"),
            text=t(key="day_end", lang=lang),
            reply_markup=markup.as_markup(),
        )


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
