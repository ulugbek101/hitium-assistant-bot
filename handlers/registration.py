from aiogram import types

from router import router


@router.message(text="Ro'yxatdan o'tish")
async def start_registration(message: types.Message):
    ...
