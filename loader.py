from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any

from config import TOKEN, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, MEDIA_ROOT, ADMINS
from utils.db_api.db import Database

db = Database(db_name=DB_NAME,
              db_user=DB_USER,
              db_password=DB_PASSWORD,
              db_host=DB_HOST,
              db_port=DB_PORT)

db.create_users_table()
db.create_days_table()
db.create_attendance_table()


class LanguageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable,
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        # Default language
        lang = "uz"

        if hasattr(event, "from_user") and event.from_user:
            lang = db.get_user_language(event.from_user.id)

        # Inject into handler
        data["lang"] = lang if lang else "uz"

        return await handler(event, data)


bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.message.middleware(LanguageMiddleware())
dp.callback_query.middleware(LanguageMiddleware())
