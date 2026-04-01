from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    lang = State()
    phone_number = State()
    first_name = State()
    last_name = State()
    middle_name = State()
    born_year = State()
    type_of_document = State()
    id_card_photo1 = State()
    id_card_photo2 = State()
    passport_photo = State()
    card_number = State()
    card_holder_name = State()
    tranzit_number = State()
    bank_name = State()
    specialization = State()
