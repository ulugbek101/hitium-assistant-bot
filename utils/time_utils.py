# utils/time_utils.py
from datetime import datetime, time
from zoneinfo import ZoneInfo

TASHKENT_TZ = ZoneInfo("Asia/Tashkent")
CUTOFF_TIME = time(21, 0)


def now_tashkent() -> datetime:
    return datetime.now(tz=TASHKENT_TZ)


def is_after_cutoff() -> bool:
    return now_tashkent().time() >= CUTOFF_TIME
