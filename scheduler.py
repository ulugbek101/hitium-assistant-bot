# scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zoneinfo import ZoneInfo

from scheduled_notifications import (
    day_start,
    day_end,
    create_working_day,
    create_attendance_for_everyday,
    auto_close_all_open_days,
)

# -------------------------------------------------
# Timezone
# -------------------------------------------------
TASHKENT_TZ = ZoneInfo("Asia/Tashkent")

# -------------------------------------------------
# Scheduler instance (SINGLETON)
# -------------------------------------------------
scheduler = AsyncIOScheduler(timezone=TASHKENT_TZ)


def start_scheduler():
    """
    Starts APScheduler and registers all cron jobs.
    Safe to call multiple times (jobs won't duplicate).
    """
    if scheduler.running:
        return

    scheduler.start()

    # -------------------------------------------------
    # Morning jobs
    # -------------------------------------------------
    scheduler.add_job(
        create_working_day,
        trigger="cron",
        hour=5,
        minute=55,
        id="create_working_day",
        replace_existing=True,
    )

    scheduler.add_job(
        create_attendance_for_everyday,
        trigger="cron",
        hour=5,
        minute=56,
        id="create_attendance_for_everyday",
        replace_existing=True,
    )

    scheduler.add_job(
        day_start,
        trigger="cron",
        hour=7,
        minute=55,
        id="day_start",
        replace_existing=True,
    )

    # -------------------------------------------------
    # Evening reminder (NOT a cutoff)
    # -------------------------------------------------
    scheduler.add_job(
        day_end,
        trigger="cron",
        hour=17,
        minute=55,
        id="day_end_reminder",
        replace_existing=True,
    )

    # -------------------------------------------------
    # 🔴 HARD CUTOFF — 21:00 Asia/Tashkent
    # -------------------------------------------------
    scheduler.add_job(
        auto_close_all_open_days,
        trigger="cron",
        hour=15,
        minute=34,
        id="attendance_cutoff_21_00",
        replace_existing=True,
    )
