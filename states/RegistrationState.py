from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    first_name = State()
    last_name = State()
    middle_name = State()
    passport_photo1 = State()
    passport_photo2 = State()
    specialization = State()
