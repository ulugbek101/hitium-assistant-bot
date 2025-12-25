from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scheduled_notifications import day_start, day_end, create_working_day, create_attendance_for_everyday

scheduler = AsyncIOScheduler()


def start_scheduler():
    scheduler.start()
    scheduler.add_job(day_start, 'cron', hour=1, minute=40)
    scheduler.add_job(day_end, 'cron', hour=17, minute=55)
    scheduler.add_job(create_working_day, 'cron', hour=4, minute=50)
    scheduler.add_job(create_attendance_for_everyday, 'cron', hour=1, minute=39)
