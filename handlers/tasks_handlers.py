from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from datetime import datetime

from keyboards import cancel_menu, tasks_menu
from states import *

from database import add_tasks, delete_task
from morning import my_tasks

router = Router()

@router.message(lambda message: message.text == "➕ Задачи")
async def tasks(message: Message, state: FSMContext):
    await message.answer(f'{await my_tasks(message.from_user.id)}', parse_mode="HTML", reply_markup=tasks_menu)

@router.message(lambda message: message.text == "📌 Мои задачи")
async def add_task(message: Message, state: FSMContext):
    await message.answer(f'{await my_tasks(message.from_user.id)}', parse_mode="HTML")

@router.message(lambda message: message.text == "✏️ Добавить задачу")
async def add_task(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AddTask.name)
    await message.answer("📌 Че у нас сегодня:", reply_markup=cancel_menu)

@router.message(AddTask.name)
async def add_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not name:
        await message.answer("❌ Название не может быть пустым.")
        return
    await state.update_data(name=name)
    await state.set_state(AddTask.deadline)
    await message.answer(
        "🕐 Теперь введи дедлайн задачи.\n\n"
        "Например:\n<code>20.10.2026</code>",
        parse_mode="HTML"
    )

@router.message(AddTask.deadline)
async def add_deadline(message: Message, state: FSMContext):
    deadline = list(map(int, (message.text or "").split('.')))

    if len(deadline) == 2:
        deadline = datetime(datetime.today().year, deadline[1], deadline[0], 23, 59)
    elif len(deadline) == 3:
        deadline = datetime(deadline[2], deadline[1], deadline[0], 23, 59)

    await state.update_data(deadline=deadline)

    data = await state.get_data()

    await add_tasks(message.from_user.id, data['name'], data['deadline'])

    await message.answer(
        f"✅ <b>Задача добавлена!</b>",
        parse_mode="HTML",
        reply_markup=tasks_menu
    )
    await state.clear()


@router.message(lambda message: message.text == "🗑 Удалить задачу")
async def del_task(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(DeleteTask.id)
    await message.answer("🗑 Введи ID задачи, которую удаляем:", reply_markup=cancel_menu)


@router.message(DeleteTask.id)
async def del_task(message: Message, state: FSMContext):
    id = (message.text or "").strip()

    await delete_task(message.from_user.id, id)

    await message.answer(
        "Задача удалена (не факт)!",
        reply_markup=tasks_menu
    )

    await state.clear()