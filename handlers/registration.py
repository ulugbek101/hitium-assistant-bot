import re

import requests

from aiogram import F
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from loader import db, bot
from config import API_URL
from router import router
from states.registration import Registration


@router.message(F.text.contains("Ro'yxatdan o'tish"))
async def start_registration(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardBuilder()
    markup.button(text="📞 Telefon raqamimni ulashish", request_contact=True)

    await message.answer(
        text="Telefon raqamingizni yuboring yoki qo'lda yozib kiriting\n"
             "Telefon raqam quyidagicha formatda yozilishi kerak:\n"
             "+998 99 693 73 08\n"
             "998 99 693 73 08\n"
             "+998996937308\n"
             "998996937308",
        reply_markup=markup.as_markup(
            one_time_keyboard=True,
            resize_keyboard=True,
        )
    )

    await state.set_state(Registration.phone_number)


@router.message(Registration.phone_number)
async def save_phone_number(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number if message.contact else message.text
    phone_number = phone_number.replace("+", "")

    pattern = re.compile(r"^998\d{9}$")

    if pattern.match(phone_number.replace("+", "").replace(" ", "")):
        # Make initial registration of a user
        try:
            db.initial_registration(telegram_id=message.from_user.id)
        except Exception as _exp:
            print("Ro'yxatga olishda xatolik yuz berdi:", _exp.__class__.__name__, _exp)
            await message.answer(text=f"Ro'yxatga olishda xatolik yuz berdi: {_exp.__class__.__name__}: {_exp}")

        await message.answer(text="Ismingizni kiriting", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Registration.first_name)

        db.update_field(telegram_id=message.from_user.id, field_name="phone_number", value=phone_number)
    else:
        await message.answer("Telefon raqam noto'g'ri formatda kiritildi, "
                             "qaytadan kiriting yoki tugmani bosish orqali yuboring")


@router.message(Registration.first_name)
async def save_first_name(message: types.Message, state: FSMContext):
    first_name = message.text

    db.update_field(telegram_id=message.from_user.id, field_name="first_name", value=first_name)

    await message.answer(text="Familiyangizni kiriting")
    await state.set_state(Registration.last_name)


@router.message(Registration.last_name)
async def save_last_name(message: types.Message, state: FSMContext):
    last_name = message.text

    db.update_field(telegram_id=message.from_user.id, field_name="last_name", value=last_name)

    await message.answer(text="Sharifingiz (Otangiz ismi) ni  kiriting, masalan: "
                              "Raxmatali o'g'li yoki Raxmataliyevich\nPassport yoki "
                              "ID kartada yozilgan holatini")
    await state.set_state(Registration.middle_name)


@router.message(Registration.middle_name)
async def save_middle_name(message: types.Message, state: FSMContext):
    middle_name = message.text

    db.update_field(telegram_id=message.from_user.id, field_name="middle_name", value=middle_name)

    markup = ReplyKeyboardBuilder()
    markup.button(text="Passport")
    markup.button(text="ID Karta")
    markup.adjust(2)

    await message.answer(
        text="Qaysi hujjat turidan foydalanasiz, Passport yoki ID karta ?",
        reply_markup=markup.as_markup(resize_keyboard=True)
    )
    await state.set_state(Registration.type_of_document)


@router.message(Registration.type_of_document)
async def save_type_of_document(message: types.Message, state: FSMContext):
    type_of_document = message.text.strip().lower()

    if type_of_document not in ["passport", "id karta"]:
        await message.answer(text="Noto'g'ri hujjat turi tanlandi, iltimos, quyida keltirilganlardan tanlang")
    else:
        type_of_document = "passport" if type_of_document == "passport" else "id_card"

        if type_of_document == "passport":
            await message.answer("Passport rasmingizni yuboring", reply_markup=types.ReplyKeyboardRemove())
            await state.set_state(Registration.passport_photo)
        else:
            await message.answer("ID Kartangizni old qismi rasmini yuboring", reply_markup=types.ReplyKeyboardRemove())
            await state.set_state(Registration.id_card_photo1)

        db.update_field(telegram_id=message.from_user.id, field_name="type_of_document", value="passport")


@router.message(Registration.passport_photo)
async def save_passport_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer(
            "Iltimos, passport rasmingizni rasm ko'rinishida yuboring, "
            "matn yoki fayl ko'rinishida emas"
        )
        return

    # Telegram sends photos as a list of sizes, take the largest one
    photo_file = message.photo[-1]
    file_id = photo_file.file_id

    db.update_field(telegram_id=message.from_user.id, field_name="passport_photo", value=file_id)

    await message.answer("Karta raqamingizni yuboring")
    await state.set_state(Registration.card_number)


@router.message(Registration.id_card_photo1)
async def save_id_card_photo1(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("Iltimos, ID Kartaning old qismi rasmini rasm ko'rinishida yuboring, matn yoki fayl "
                             "ko'rinishida emas")
        return

    file_id = message.photo[-1].file_id

    db.update_field(telegram_id=message.from_user.id, field_name="id_card_photo1", value=file_id)

    await message.answer("ID Kartaning orqa qismi rasmini yuboring")
    await state.set_state(Registration.id_card_photo2)


@router.message(Registration.id_card_photo2)
async def save_id_card_photo2(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("Iltimos, ID Kartaning orqa qismi rasmini rasm ko'rinishida yuboring, matn yoki fayl "
                             "ko'rinishida emas")
        return

    file_id = message.photo[-1].file_id

    db.update_field(telegram_id=message.from_user.id, field_name="id_card_photo2", value=file_id)

    await message.answer("Karta raqamingizni yuboring")
    await state.set_state(Registration.card_number)


@router.message(Registration.card_number)
async def save_card_number(message: types.Message, state: FSMContext):
    card_number = message.text.strip().replace(" ", "")

    if not card_number or len(card_number) < 16 or not card_number.isdigit():
        await message.answer("Karta raqami noto'g'ri formatda kiritildi")
        return

    db.update_field(telegram_id=message.from_user.id, field_name="card_number", value=card_number)
    await message.answer("Karta egasi kim bo'lib chiqadi ? Ism va Familiyani to'liq yozing")
    await state.set_state(Registration.card_holder_name)


@router.message(Registration.card_holder_name)
async def save_card_holder_name(message: types.Message, state: FSMContext):
    card_holder_name = message.text.strip()

    if not card_holder_name or len(card_holder_name.split()) < 2:
        await message.answer("Ism va Familiya kiritilishi shart")
        return

    db.update_field(telegram_id=message.from_user.id, field_name="card_holder_name", value=card_holder_name)
    await message.answer("Tranzit raqamingizni kiriting (Yuridik shaxslar uchun)")
    await state.set_state(Registration.tranzit_number)


@router.message(Registration.tranzit_number)
async def save_tranzit_number(message: types.Message, state: FSMContext):
    tranzit_number = message.text.strip().replace(" ", "")

    if not tranzit_number or not tranzit_number.isdigit():
        await message.answer("Tranzit raqam noto'g'ri formatda kiritildi")
        return

    db.update_field(telegram_id=message.from_user.id, field_name="tranzit_number", value=tranzit_number)
    await message.answer("Bank nomini kiriting")
    await state.set_state(Registration.bank_name)


@router.message(Registration.bank_name)
async def save_bank_name(message: types.Message, state: FSMContext):
    bank_name = message.text.strip()

    db.update_field(telegram_id=message.from_user.id, field_name="bank_name", value=bank_name)
    await message.answer("Mutaxassisligingizni kiriting")
    await state.set_state(Registration.specialization)


@router.message(Registration.specialization)
async def save_specialization(message: types.Message, state: FSMContext):
    specialization = message.text.strip()

    db.update_field(telegram_id=message.from_user.id, field_name="specialization", value=specialization)
    await message.answer("Iltimos, ozgina kuting ...")
    await state.clear()

    await register_user(telegram_id=message.from_user.id)


async def register_user(telegram_id: int):
    user = db.get_user(telegram_id=telegram_id)
    URL = f"{API_URL}/register-user/"
    response = requests.post(URL, json=user)

    if response.ok:
        await bot.send_message(
            telegram_id=telegram_id,
            text="✅ Ma'lumotlaringiz muvaffaqiyatli saqlandi, raxmat",
        )
    else:
        await bot.send_message(
            telegram_id=telegram_id,
            text="Ro'yxatga olishda xatolik yuz berdi, iltimos, dasturchi bilan bog'laning\n"
                 f"Xatolik statusi: {response.status_code}",
        )
