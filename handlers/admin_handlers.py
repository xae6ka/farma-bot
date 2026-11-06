from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import add_admin, get_all_users, is_admin, get_active_users
from keyboards import admin_menu

from tabulate import tabulate
from html import escape

import os
from dotenv import load_dotenv

router = Router()

#admin_panel
@router.message(Command("admin"))
async def start(message: Message):
    await add_admin(
        user_id=message.from_user.id,
        first_name=message.from_user.first_name
    )

    if message.text.split(' ')[1] == os.getenv("ADMIN_PASSWORD"):
        await message.answer(
                f"Бля, ты админ",
                parse_mode="HTML",
                reply_markup=admin_menu
            )
    else:
        await message.answer(message.text.split(' ')[1])


@router.message(lambda message: message.text == "📕 Отчет")
async def add_task(message: Message, state: FSMContext):
    if (await is_admin(message.from_user.id)) != []:
        users = await get_all_users()
        active_users = await get_active_users()

        headers = ["Имя", "Username", "Sub"]

        rows = []

        for user in active_users:
            rows.append([
                escape(str(user[1] or "-")),
                escape(f"@{user[3]}" if user[3] else "-"),
                "⭐" if str(user[4]) == "1" else "Нет"
            ])

        table = tabulate(
            rows,
            headers=headers,
            tablefmt="simple",
            colalign=("left", "left", "center")
        )


        text = f"""
<b>📕 | ОТЧЕТ</b>

Общее кол-во пользователей: {len(users)}
Количество активных пользователей: {len(active_users)}
Активные / все: {int((len(active_users)/len(users))*100)}%
Админ права: {(await is_admin(message.from_user.id)) != []}
Версия: {os.getenv("VERSION")}

Таблица пользователей:

<pre>{table}</pre>
"""
        
        await message.answer(text, parse_mode="HTML")


@router.message(lambda message: message.text == "📚 Полный список пользователей")
async def add_task(message: Message, state: FSMContext):
    if (await is_admin(message.from_user.id)) != []:
        users = await get_all_users()

        headers = ["Имя", "Username", "Sub"]

        rows = []

        for user in users:
            rows.append([
                escape(str(user[1] or "-")),
                escape(f"@{user[3]}" if user[3] else "-"),
                "⭐" if str(user[4]) == "1" else "Нет"
            ])

        table = tabulate(
            rows,
            headers=headers,
            tablefmt="simple",
            colalign=("left", "left", "center")
        )
        
        await message.answer(f'<b>📚 | Полный список пользователей</b>\n\nТаблица пользователей:\n\n<pre>{table}</pre>', parse_mode="HTML")