import datetime
import aiohttp

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from i18n.translate import t
from router import router

from config import API_URL


@router.message(lambda message: message.text == "/tasks")
async def get_tasks(message: types.Message, lang: str):
    """
    Fetch tasks from /tasks/ endpoint for a given telegram_id.
    """

    params = {"telegram_id": message.from_user.id}

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/tasks/", params=params) as resp:
            if resp.status == 200:
                tasks = await resp.json()

                if len(tasks) == 0:
                    await message.answer(t("no_tasks_found"), lang)
                    return

                for i, task in enumerate(tasks, start=1):
                    is_done = task.get("is_done")
                    if is_done:
                        continue

                    task_text = ""
                    name = task.get(f"name")
                    description = task.get(f"description")
                    deadline = task.get("deadline")

                    task_text += f"\n<b>{i}) {name}</b>\n"
                    task_text += f"\n{t('description')}: <b>{description}</b>\n"
                    task_text += f"\n{t('deadline')}: <b>{deadline}</b>\n"

                    # Create an empty keyboard with no buttons
                    markup = InlineKeyboardBuilder()

                    # Check if user is a foreman in any brigade
                    show_markup = any(
                        brigade.get("foreman", {}).get("telegram_id") == str(message.from_user.id)
                        for brigade in task.get("brigades", [])
                    )

                    # Add a button to complete a task only if user is a foreman (Бригадир)
                    if show_markup:
                        markup.button(text=t("work_completed_btn"), callback_data=f"work_completed:{task.get('id')}")

                    await message.answer(text=task_text, parse_mode="HTML", reply_markup=markup.as_markup())

            else:
                return None
