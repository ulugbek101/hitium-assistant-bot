import os
import re
import datetime

from aiogram import types
from aiogram.client.session import aiohttp
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiohttp import ClientTimeout

from enums import languages
from i18n.translate import t
from loader import db, bot
from config import API_URL
from router import router
from states.registration import Registration
from utils.helpers import download_photo


HTTP_TIMEOUT = ClientTimeout(total=15)


@router.message(Registration.lang)
async def save_language(message: types.Message, state: FSMContext, lang: str):
    selected_lang = languages.get(message.text.strip())

    if not selected_lang:
        await message.answer(t("wrong_language_warning", lang=lang))
        return

    try:
        db.initial_registration(telegram_id=message.from_user.id)
    except Exception:
        await message.answer(
            t("already_registered_warning", selected_lang).format(
                fullname=message.from_user.full_name.title()
            )
        )

    db.update_user_field(telegram_id=message.from_user.id, field_name="lang", value=selected_lang)

    kb = ReplyKeyboardBuilder()
    kb.button(text=t("phone_number_btn", selected_lang), request_contact=True)

    await message.answer(
        t("phone_number_description", selected_lang),
        reply_markup=kb.as_markup(resize_keyboard=True, one_time_keyboard=True),
    )

    await state.set_state(Registration.phone_number)


@router.message(Registration.phone_number)
async def save_phone_number(message: types.Message, state: FSMContext, lang: str):
    phone_number = message.contact.phone_number if message.contact else message.text
    phone_number = phone_number.replace("+", "").replace(" ", "")

    if not re.fullmatch(r"998\d{9}", phone_number):
        await message.answer(t("invalid_phone_number", lang))
        return

    db.update_user_field(telegram_id=message.from_user.id, field_name="phone_number", value=phone_number)

    await message.answer(t("request_first_name", lang), reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Registration.first_name)


@router.message(Registration.first_name)
async def save_first_name(message: types.Message, state: FSMContext, lang: str):
    db.update_user_field(telegram_id=message.from_user.id, field_name="first_name",
                         value=message.text.strip().capitalize())

    await message.answer(t("request_last_name", lang))
    await state.set_state(Registration.last_name)


@router.message(Registration.last_name)
async def save_last_name(message: types.Message, state: FSMContext, lang: str):
    db.update_user_field(telegram_id=message.from_user.id, field_name="last_name",
                         value=message.text.strip().capitalize())

    await message.answer(t("request_middle_name", lang))
    await state.set_state(Registration.middle_name)


@router.message(Registration.middle_name)
async def save_middle_name(message: types.Message, state: FSMContext, lang: str):
    db.update_user_field(telegram_id=message.from_user.id, field_name="middle_name",
                         value=message.text.strip().capitalize())

    await message.answer(
        t("request_born_year", lang),
    )

    await state.set_state(Registration.born_year)


@router.message(Registration.born_year)
async def save_age(message: types.Message, state: FSMContext, lang: str):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", message.text.strip()):
        await message.answer(t("invalid_age", lang))
        return

    db.update_user_field(telegram_id=message.from_user.id, field_name="born_year", value=message.text.strip())

    kb = ReplyKeyboardBuilder()
    kb.button(text=t("passport_btn", lang))
    kb.button(text=t("id_card", lang))
    kb.adjust(2)

    await message.answer(t("request_document_type", lang), reply_markup=kb.as_markup(resize_keyboard=True))
    await state.set_state(Registration.type_of_document)


@router.message(Registration.type_of_document)
async def save_type_of_document(message: types.Message, state: FSMContext, lang: str):
    text = message.text.lower()

    if "passport" in text or "паспорт" in text:
        doc_type = "passport"
        await message.answer(t("passport_photo_request", lang), reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Registration.passport_photo)

    elif "id" in text:
        doc_type = "id_card"
        await message.answer(t("id_card_front_request", lang), reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Registration.id_card_photo1)

    else:
        await message.answer(t("invalid_document_type", lang))
        return

    db.update_user_field(telegram_id=message.from_user.id, field_name="type_of_document", value=doc_type)


@router.message(Registration.passport_photo)
async def save_passport_photo(message: types.Message, state: FSMContext, lang: str):
    if not message.photo:
        await message.answer(t("invalid_photo_type", lang))
        return

    path = await download_photo(bot=bot, message=message, is_passport=True)

    db.update_user_field(telegram_id=message.from_user.id, field_name="passport_photo", value=path)

    await message.answer(t("request_card_number", lang))
    await state.set_state(Registration.card_number)


@router.message(Registration.id_card_photo1)
async def save_id_card_photo1(message: types.Message, state: FSMContext, lang: str):
    if not message.photo:
        await message.answer(t("invalid_photo_type", lang))
        return

    path = await download_photo(bot=bot, message=message, side="front")

    db.update_user_field(telegram_id=message.from_user.id, field_name="id_card_photo1", value=path)

    await message.answer(t("id_card_back_request", lang))
    await state.set_state(Registration.id_card_photo2)


@router.message(Registration.id_card_photo2)
async def save_id_card_photo2(message: types.Message, state: FSMContext, lang: str):
    if not message.photo:
        await message.answer(t("invalid_photo_type", lang))
        return

    path = await download_photo(bot=bot, message=message, side="back")

    db.update_user_field(telegram_id=message.from_user.id, field_name="id_card_photo2", value=path)

    await message.answer(t("request_card_number", lang))
    await state.set_state(Registration.card_number)


@router.message(Registration.card_number)
async def save_card_number(message: types.Message, state: FSMContext, lang: str):
    number = message.text.replace(" ", "")

    if not re.fullmatch(r"\d{16}", number):
        await message.answer(t("invalid_card_number", lang))
        return

    db.update_user_field(telegram_id=message.from_user.id, field_name="card_number", value=number)

    await message.answer(t("request_card_holder_name", lang))
    await state.set_state(Registration.card_holder_name)


@router.message(Registration.card_holder_name)
async def save_card_holder_name(message: types.Message, state: FSMContext, lang: str):
    name = message.text.strip().title()

    if len(name.split()) < 2:
        await message.answer(t("invalid_card_holder_name", lang))
        return

    db.update_user_field(telegram_id=message.from_user.id, field_name="card_holder_name", value=name)

    await message.answer(t("request_tranzit_number", lang))
    await state.set_state(Registration.tranzit_number)


@router.message(Registration.tranzit_number)
async def save_tranzit_number(message: types.Message, state: FSMContext, lang: str):
    value = message.text.replace(" ", "")

    if not value.isdigit():
        await message.answer(t("invalid_tranzit_number", lang))
        return

    db.update_user_field(telegram_id=message.from_user.id, field_name="tranzit_number", value=value)

    await message.answer(t("request_bank_name", lang))
    await state.set_state(Registration.bank_name)


@router.message(Registration.bank_name)
async def save_bank_name(message: types.Message, state: FSMContext, lang: str):
    db.update_user_field(telegram_id=message.from_user.id, field_name="bank_name", value=message.text.strip().upper())

    markup = ReplyKeyboardBuilder()

    async with aiohttp.ClientSession(timeout=HTTP_TIMEOUT) as session:
        async with session.get(f"{API_URL}/specializations/") as r:
            if r.status == 200:
                specialization_names = await r.json()

                for specialization_name in specialization_names:
                    markup.button(text=specialization_name)
                markup.adjust(2)

            else:
                await message.answer(text=t("specializations_fetch_fail", lang=lang))

    await message.answer(t("request_specialization", lang), reply_markup=markup.as_markup(resize_keyboard=True, one_time_keyboard=True))
    await state.set_state(Registration.specialization)


@router.message(Registration.specialization)
async def save_specialization(message: types.Message, state: FSMContext, lang: str):
    db.update_user_field(telegram_id=message.from_user.id, field_name="specialization",
                         value=message.text.strip().capitalize())

    async with aiohttp.ClientSession(timeout=HTTP_TIMEOUT) as session:
        async with session.get(f"{API_URL}/specializations/") as r:
            if r.status == 200:
                specialization_names = await r.json()
                specialization_names = list(map(lambda name: name.lower(), specialization_names))

                if message.text.lower() not in specialization_names:
                    await message.answer(text=t("invalid_specialization", lang=lang))
                    return

            else:
                await message.answer(text=t("specializations_fetch_fail", lang=lang))
                return

    await message.answer(t("registration_wait", lang), reply_markup=ReplyKeyboardRemove())
    await state.clear()

    await register_user(message.from_user.id)


async def register_user(telegram_id: int):
    user = db.get_user(telegram_id)
    form = aiohttp.FormData()

    for field in [
        "telegram_id", "first_name", "last_name", "middle_name",
        "phone_number", "type_of_document", "card_number",
        "card_holder_name", "tranzit_number",
        "bank_name", "specialization", "born_year"
    ]:
        value = user.get(field)

        if isinstance(value, datetime.date):
            value = value.isoformat()

        if value is not None:
            form.add_field(field, str(value))

    files = []

    if user["type_of_document"] == "passport":
        path = user.get("passport_photo")
        if path and os.path.exists(path):
            f = open(path, "rb")
            files.append(f)
            form.add_field("passport_photo", f, filename=os.path.basename(path))

    else:
        for key in ("id_card_photo1", "id_card_photo2"):
            path = user.get(key)
            if path and os.path.exists(path):
                f = open(path, "rb")
                files.append(f)
                form.add_field(key, f, filename=os.path.basename(path))

    async with aiohttp.ClientSession(timeout=HTTP_TIMEOUT) as session:
        async with session.post(f"{API_URL}/register-user/", data=form) as r:
            if r.status == 200:
                await bot.send_message(telegram_id, t("registration_success", user["lang"]))
            else:
                await bot.send_message(telegram_id, t("registration_error", user["lang"]))

    for f in files:
        f.close()
