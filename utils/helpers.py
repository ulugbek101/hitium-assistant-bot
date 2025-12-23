from datetime import datetime
import os

from aiogram import types, Bot

from config import MEDIA_ROOT


async def download_photo(bot: Bot, message: types.Message, is_passport: bool, side: str = "front") -> str:
    """
    Function to download photo to local file store folder
    """

    # Get the highest quality photo
    photo = message.photo[-1]

    # Get file info from Telegram
    file = await bot.get_file(photo.file_id)

    # Create unique filename (telegram_id.jpg)
    if is_passport:
        filename = f"{message.from_user.id}.jpg"
    else:
        filename = f"id_{side}_{message.from_user.id}.jpg"

    file_path = os.path.join(MEDIA_ROOT, filename)

    # Download file to local storage
    await bot.download_file(file.file_path, file_path)
    return file_path


def check_working_day():
    """
    Checks whether today is working day or not
    """
    return datetime.now().weekday() + 1 in range(1, 7)
