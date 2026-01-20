from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy import create_engine
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
engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    pool_pre_ping=True,   # 🔥 detects dead connections
    pool_recycle=1800,    # 🔥 recycle every 30 min
    pool_size=5,
    max_overflow=10,
)

jobstores = {
    "default": SQLAlchemyJobStore(engine=engine)
}

job_defaults = {
    "coalesce": True,
    "misfire_grace_time": 600,  # 10 minutes
}

# -------------------------------------------------
# Scheduler instance (SINGLETON)
# -------------------------------------------------
scheduler = AsyncIOScheduler(
    timezone=TASHKENT_TZ,
    jobstores=jobstores,
    job_defaults=job_defaults,
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
        hour=20,
        minute=57,
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
