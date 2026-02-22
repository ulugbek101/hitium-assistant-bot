import logging

import aiohttp
from aiohttp import FormData

from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext

from config import API_URL
from i18n.translate import t
from loader import dp, db
from states.task import TaskState
from utils.helpers import download_photo_from_telegram


@dp.callback_query(lambda call: "work_completed" in call.data)
async def finish_task(call: types.CallbackQuery, lang: str, state: FSMContext):
    task_id = int(call.data.split(":")[-1])

    # Update task's id internally
    await state.set_state(TaskState.task_id)
    await state.update_data(task_id=task_id)

    markup = ReplyKeyboardBuilder()
    markup.button(text=t("work_completed_description_btn", lang))

    await state.set_state(TaskState.description)
    await call.message.answer(
        text=t("request_work_completed_description_optional", lang),
        reply_markup=markup.as_markup(resize_keyboard=True, one_time_keyboard=True),
    )

    # TODO: Remove after test
    await call.message.delete_reply_markup()


@dp.message(TaskState.description)
async def save_task_description(message: types.Message, lang: str, state: FSMContext):
    if not message.text == t("work_completed_description_btn", lang):
        await state.update_data(description=message.text.strip())

    await state.set_state(TaskState.photo)
    await message.answer(text=t("request_work_completed_photo", lang),
                         reply_markup=types.ReplyKeyboardRemove())


@dp.message(TaskState.photo)
async def save_task_photos(message: types.Message, lang: str, state: FSMContext):
    if message.photo:
        data = await state.get_data()
        task_id = int(data["task_id"])
        description = (data.get("description") or "").strip()
        file_id = message.photo[-1].file_id
        worker_telegram_id = str((db.get_user(message.from_user.id) or {}).get("telegram_id") or "")

        if not worker_telegram_id:
            await message.answer(t("worker_not_found", lang))
            return

        try:
            buf = await download_photo_from_telegram(message.bot, file_id)
            filename = f"task_{task_id}.jpg"

            status = await send_work_completed(task_id=task_id, photo_buf=buf, worker_telegram_id=str(worker_telegram_id), description=description, filename=filename)

            if status == 200:
                await message.answer(t("finished_work_details_sent_for_review", lang))
            elif status == 500:
                await message.answer(t("something_went_wrong_on_backend", lang))

        except Exception as e:
            await message.answer(t("error_while_sending_details", lang).format(e))
            return

        finally:
            await state.clear()
    else:
        await message.answer(text=t("invalid_task_photo", lang))


async def send_work_completed(task_id: int, photo_buf, worker_telegram_id: str, description: str = "", filename: str = "photo.jpg"):
    form = FormData()

    form.add_field("task_id", str(task_id))
    form.add_field("description", description)
    form.add_field("worker_telegram_id", worker_telegram_id)
    form.add_field(
        name="photo",
        value=photo_buf.getvalue(),
        filename=filename,
        content_type="image/jpeg",
    )

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/save-finished-word-details/", data=form) as resp:
            body = await resp.text()

            if resp.status != 200:
                logging.error("Error while sending finished work details: " + str(await resp.json()))
                return 500

            logging.info("Finished work details saved successfully: " + str(await resp.json()))
            return 200

