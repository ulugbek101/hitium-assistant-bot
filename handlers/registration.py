import os
import re

from aiogram import F
from aiogram import types
from aiogram.client.session import aiohttp
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from enums import languages
from i18n.translate import t
from loader import db, bot
from config import API_URL
from router import router
from states.registration import Registration
from utils.helpers import download_photo


@router.message(Registration.lang)
async def save_language(message: types.Message, state: FSMContext, lang):
    selected_lang = languages.get(message.text.strip())

    if not selected_lang:
        await message.answer(
            text=t("wrong_language_warning", lang)
        )
        return

    # Make initial registration of a user
    try:
        db.initial_registration(telegram_id=message.from_user.id)
    except Exception as _exp:
        await message.answer(text=t("already_registered_warning", selected_lang).format(fullname=message.from_user.full_name.title()))

    db.update_field(telegram_id=message.from_user.id, field_name="lang", value=selected_lang)

    markup = ReplyKeyboardBuilder()
    markup.button(text=t("phone_number_btn", selected_lang), request_contact=True)

    await message.answer(
        text=t("phone_number_description", selected_lang),
        reply_markup=markup.as_markup(
            one_time_keyboard=True,
            resize_keyboard=True,
        )
    )

    await state.set_state(Registration.phone_number)


@router.message(Registration.phone_number)
async def save_phone_number(message: types.Message, state: FSMContext, lang: str):
    phone_number = message.contact.phone_number if message.contact else message.text
    phone_number = phone_number.replace("+", "")

    pattern = re.compile(r"^998\d{9}$")

    if pattern.match(phone_number.replace("+", "").replace(" ", "")):
        await message.answer(text=t("request_first_name", lang), reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Registration.first_name)

        db.update_field(telegram_id=message.from_user.id, field_name="phone_number", value=phone_number)
    else:
        await message.answer(t("invalid_phone_number", lang))


@router.message(Registration.first_name)
async def save_first_name(message: types.Message, state: FSMContext, lang: str):
    first_name = message.text.capitalize()

    db.update_field(telegram_id=message.from_user.id, field_name="first_name", value=first_name)

    await message.answer(text=t("request_last_name", lang))
    await state.set_state(Registration.last_name)


@router.message(Registration.last_name)
async def save_last_name(message: types.Message, state: FSMContext, lang: str):
    last_name = message.text.capitalize()

    db.update_field(telegram_id=message.from_user.id, field_name="last_name", value=last_name)

    await message.answer(text=t("request_age", lang))
    await state.set_state(Registration.age)


@router.message(Registration.age)
async def save_age(message: types.Message, state: FSMContext, lang: str):
    age = message.text.strip()

    pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    if not pattern.match(age):
        await message.answer(text=t("invalid_age", lang))
        return

    db.update_field(telegram_id=message.from_user.id, field_name="age", value=age)

    await message.answer(text=t("request_middle_name", lang))
    await state.set_state(Registration.age)


@router.message(Registration.middle_name)
async def save_middle_name(message: types.Message, state: FSMContext, lang: str):
    middle_name = message.text.capitalize()

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
async def save_type_of_document(message: types.Message, state: FSMContext, lang: str):
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
async def save_passport_photo(message: types.Message, state: FSMContext, lang: str):
    if not message.photo:
        await message.answer(
            "Iltimos, passport rasmingizni rasm ko'rinishida yuboring, "
            "matn yoki fayl ko'rinishida emas"
        )
        return

    file_path = await download_photo(bot=bot, message=message, is_passport=False)

    db.update_field(telegram_id=message.from_user.id, field_name="passport_photo", value=file_path)

    await message.answer("Karta raqamingizni yuboring")
    await state.set_state(Registration.card_number)


@router.message(Registration.id_card_photo1)
async def save_id_card_photo1(message: types.Message, state: FSMContext, lang: str):
    if not message.photo:
        await message.answer("Iltimos, ID Kartaning old qismi rasmini rasm ko'rinishida yuboring, matn yoki fayl "
                             "ko'rinishida emas")
        return

    file_path = await download_photo(bot=bot, message=message, is_passport=False, side="front")

    db.update_field(telegram_id=message.from_user.id, field_name="id_card_photo1", value=file_path)

    await message.answer("ID Kartaning orqa qismi rasmini yuboring")
    await state.set_state(Registration.id_card_photo2)


@router.message(Registration.id_card_photo2)
async def save_id_card_photo2(message: types.Message, state: FSMContext, lang: str):
    if not message.photo:
        await message.answer("Iltimos, ID Kartaning orqa qismi rasmini rasm ko'rinishida yuboring, matn yoki fayl "
                             "ko'rinishida emas")
        return

    file_path = await download_photo(bot=bot, message=message, is_passport=False, side="back")

    db.update_field(telegram_id=message.from_user.id, field_name="id_card_photo2", value=file_path)

    await message.answer("Karta raqamingizni yuboring")
    await state.set_state(Registration.card_number)


@router.message(Registration.card_number)
async def save_card_number(message: types.Message, state: FSMContext, lang: str):
    card_number = message.text.strip().replace(" ", "")

    if not card_number or len(card_number) < 16 or not card_number.isdigit():
        await message.answer("Karta raqami noto'g'ri formatda kiritildi")
        return

    db.update_field(telegram_id=message.from_user.id, field_name="card_number", value=card_number)
    await message.answer("Karta egasi kim bo'lib chiqadi ? Ism va Familiyani to'liq yozing")
    await state.set_state(Registration.card_holder_name)


@router.message(Registration.card_holder_name)
async def save_card_holder_name(message: types.Message, state: FSMContext, lang: str):
    card_holder_name = message.text.strip().title()

    if not card_holder_name or len(card_holder_name.split()) < 2:
        await message.answer("Ism va Familiya kiritilishi shart")
        return

    db.update_field(telegram_id=message.from_user.id, field_name="card_holder_name", value=card_holder_name)
    await message.answer("Tranzit raqamingizni kiriting (Yuridik shaxslar uchun)")
    await state.set_state(Registration.tranzit_number)


@router.message(Registration.tranzit_number)
async def save_tranzit_number(message: types.Message, state: FSMContext, lang: str):
    tranzit_number = message.text.strip().replace(" ", "")

    if not tranzit_number or not tranzit_number.isdigit():
        await message.answer("Tranzit raqam noto'g'ri formatda kiritildi")
        return

    db.update_field(telegram_id=message.from_user.id, field_name="tranzit_number", value=tranzit_number)
    await message.answer("Bank nomini kiriting")
    await state.set_state(Registration.bank_name)


@router.message(Registration.bank_name)
async def save_bank_name(message: types.Message, state: FSMContext, lang: str):
    bank_name = message.text.strip().upper()

    db.update_field(telegram_id=message.from_user.id, field_name="bank_name", value=bank_name)
    await message.answer("Mutaxassisligingizni kiriting")
    await state.set_state(Registration.specialization)


@router.message(Registration.specialization)
async def save_specialization(message: types.Message, state: FSMContext, lang: str):
    specialization = message.text.strip().capitalize()

    db.update_field(telegram_id=message.from_user.id, field_name="specialization", value=specialization)
    await message.answer("Iltimos, ozgina kuting ...")
    await state.clear()

    await register_user(telegram_id=message.from_user.id)


async def register_user(telegram_id: int):
    user = db.get_user(telegram_id=telegram_id)
    document_type = user.get("type_of_document")

    URL = f"{API_URL}/register-user/"
    form = aiohttp.FormData()

    user_fields = ["telegram_id", "first_name", "last_name", "middle_name",
                   "phone_number", "type_of_document", "card_number", "card_holder_name",
                   "tranzit_number", "bank_name", "specialization", "age", "born_year"]

    for field in user_fields:
        form.add_field(field, user.get(field))

    files_to_close = []

    if document_type == "passport":
        passport_path = user.get("passport_photo")

        if passport_path and os.path.exists(os.path.abspath(passport_path)):
            photo_file = open(os.path.abspath(passport_path), "rb")
            files_to_close.append(photo_file)
            form.add_field(
                name="passport_photo",
                value=photo_file,
                filename=os.path.basename(passport_path),
                content_type="image/jpeg",
            )

    elif document_type == "id_card":
        id_front_path = user.get("id_card_photo1")
        id_back_path = user.get("id_card_photo2")

        if id_front_path and os.path.exists(os.path.abspath(id_front_path)):
            photo_file = open(os.path.abspath(id_front_path), "rb")
            files_to_close.append(photo_file)
            form.add_field(
                name="id_card_photo1",
                value=photo_file,
                filename=os.path.basename(id_front_path),
                content_type="image/jpeg",
            )

        if id_back_path and os.path.exists(os.path.abspath(id_back_path)):
            photo_file = open(os.path.abspath(id_back_path), "rb")
            files_to_close.append(photo_file)
            form.add_field(
                name="id_card_photo2",
                value=photo_file,
                filename=os.path.basename(id_back_path),
                content_type="image/jpeg",
            )

    async with aiohttp.ClientSession() as session:
        async with session.post(URL, data=form) as response:
            if response.status == 200:
                await bot.send_message(
                    telegram_id,
                    "✅ Ma'lumotlaringiz muvaffaqiyatli saqlandi, rahmat",
                )
            else:
                text = await response.text()
                await bot.send_message(
                    telegram_id,
                    "❌ Ro'yxatga olishda xatolik yuz berdi\n"
                    f"Status: {response.status}\n"
                    f"Response: {text}",
                )

    for f in files_to_close:
        f.close()
