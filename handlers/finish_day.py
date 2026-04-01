from aiogram import types

from router import router


@router.message(lambda message: message.text == "/finish_day")
async def finish_day(message: types.Message, lang: str):
    """
    Function that represents that the worker is finishing working day earlier
    """
    pass
