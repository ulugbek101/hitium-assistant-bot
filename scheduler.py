from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from zoneinfo import ZoneInfo

from loader import DB_NAME, DB_HOST, DB_USER, DB_PASSWORD, DB_PORT

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
# JobStore (DB-backed)
# -------------------------------------------------
jobstores = {
    "default": SQLAlchemyJobStore(
        # PostgreSQL (PROD):
        # url="postgresql+psycopg2://user:password@localhost:5432/hitium_bot_jobs"

        # MySQL (PROD):
        url=f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

        # SQLite (DEV ONLY):
        # url="sqlite:///hitium_bot_jobs.sqlite"
    )
}


# -------------------------------------------------
# Scheduler instance (SINGLETON)
# -------------------------------------------------
scheduler = AsyncIOScheduler(
    timezone=TASHKENT_TZ,
    jobstores=jobstores,
)


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
        minute=50,
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
        hour=21,
        minute=0,
        id="attendance_cutoff_21_00",
        replace_existing=True,
    )
