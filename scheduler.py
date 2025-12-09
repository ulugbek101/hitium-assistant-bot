from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scheduled_notifications import day_start

scheduler = AsyncIOScheduler()


def start_scheduler():
    scheduler.add_job(day_start, 'cron', hour=7, minute=55)
    scheduler.start()
