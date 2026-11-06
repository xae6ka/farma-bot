from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards import main_menu, cancel_menu, pills_menu
from states import *

from scheduler import add_reminder, remove_reminders, schedule_snooze

from database import (
    add_pill, get_pills, get_pill, delete_pill, update_schedule,
    get_dose_event, mark_dose_taken, mark_dose_snoozed
)


router = Router()

# Таблетки пить
@router.message(lambda message: message.text == "💊 Таблетки")
async def pills(message: Message, state: FSMContext):
    print("LOGGING: use func list_pills")

    pills = await get_pills(message.from_user.id)
    if not pills:
        await message.answer("💊 <b>У тебя сейчас нет активных таблеток.</b>", parse_mode="HTML", reply_markup=pills_menu)
        return

    result = "💊 <b>Твои текущие таблетки</b>\n\n"
    current_id = None
    number = 0
    for pill_id, name, time in pills:
        if pill_id != current_id:
            number += 1
            result += f"<b>{number}. {name}</b>\n"
            current_id = pill_id
        if time:
            result += f"   🕐 {time}\n"

    await message.answer(result, parse_mode="HTML", reply_markup=pills_menu)



@router.message(lambda message: message.text == "➕ Добавить таблетку")
async def add_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AddPill.name)
    await message.answer("💊 Введи название таблетки:", reply_markup=cancel_menu)


@router.message(AddPill.name)
async def add_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not name:
        await message.answer("❌ Название не может быть пустым.")
        return
    await state.update_data(name=name)
    await state.set_state(AddPill.times)
    await message.answer(
        "🕐 Теперь введи время приёма.\n\nМожно указать несколько приёмов через пробел.\n\n"
        "Например:\n<code>08:00 14:00 20:00</code>",
        parse_mode="HTML"
    )

@router.message(AddPill.times)
async def add_times(message: Message, state: FSMContext):
    times = (message.text or "").split()
    if not validate_times(times):
        await message.answer("❌ Неверный формат времени.\n\nИспользуй: <code>08:00 14:00 20:00</code>", parse_mode="HTML")
        return

    times = normalize_times(times)
    data = await state.get_data()
    pill_name = data["name"]
    user_id = message.from_user.id

    pill_id = await add_pill(user_id, pill_name, times)
    for time in times:
        add_reminder(message.bot, pill_id, user_id, pill_name, time)

    await state.clear()
    await message.answer(
        f"✅ <b>Таблетка добавлена!</b>\n\n💊 {pill_name}\n🕐 Время: {', '.join(times)}\n\n"
        "Напоминание придёт за 5 минут и точно в назначенное время.",
        parse_mode="HTML", reply_markup=main_menu
    )


def validate_times(times: list[str]):
    if not times:
        return False
    for time in times:
        parts = time.split(":")
        if len(parts) != 2:
            return False
        try:
            hour, minute = int(parts[0]), int(parts[1])
        except ValueError:
            return False
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return False
    return True


def normalize_times(times: list[str]):
    return sorted(set(f"{int(t.split(':')[0]):02d}:{int(t.split(':')[1]):02d}" for t in times))


@router.message(AddPill.times)
async def add_times(message: Message, state: FSMContext):
    times = (message.text or "").split()
    if not validate_times(times):
        await message.answer("❌ Неверный формат времени.\n\nИспользуй: <code>08:00 14:00 20:00</code>", parse_mode="HTML")
        return

    times = normalize_times(times)
    data = await state.get_data()
    pill_name = data["name"]
    user_id = message.from_user.id

    pill_id = await add_pill(user_id, pill_name, times)
    for time in times:
        add_reminder(message.bot, pill_id, user_id, pill_name, time)

    await state.clear()
    await message.answer(
        f"✅ <b>Таблетка добавлена!</b>\n\n💊 {pill_name}\n🕐 Время: {', '.join(times)}\n\n"
        "Напоминание придёт за 5 минут и точно в назначенное время.",
        parse_mode="HTML", reply_markup=main_menu
    )


@router.message(lambda message: message.text == "💊 Мои таблетки")
async def list_pills(message: Message):
    print("LOGGING: use func list_pills")

    pills = await get_pills(message.from_user.id)
    if not pills:
        await message.answer("💊 <b>У тебя сейчас нет активных таблеток.</b>", parse_mode="HTML", reply_markup=pills_menu)
        return

    result = "💊 <b>Твои текущие таблетки</b>\n\n"
    current_id = None
    number = 0
    for pill_id, name, time in pills:
        if pill_id != current_id:
            number += 1
            result += f"<b>{number}. {name}</b>\n"
            current_id = pill_id
        if time:
            result += f"   🕐 {time}\n"

    await message.answer(result, parse_mode="HTML", reply_markup=pills_menu)


@router.message(lambda message: message.text == "🗑 Удалить таблетку")
async def delete_start(message: Message, state: FSMContext):
    await state.clear()
    pills = await get_pills(message.from_user.id)
    if not pills:
        await message.answer("💊 У тебя нет таблеток для удаления.", reply_markup=main_menu)
        return

    result = "🗑 <b>Выбери таблетку для удаления</b>\n\n"
    current_id = None
    number = 0
    for pill_id, name, time in pills:
        if pill_id != current_id:
            number += 1
            result += f"{number}. {name} — ID: <code>{pill_id}</code>\n"
            current_id = pill_id
    result += "\nВведи ID таблетки:"
    await state.set_state(DeletePill.id)
    await message.answer(result, parse_mode="HTML", reply_markup=cancel_menu)


@router.message(DeletePill.id)
async def delete_confirm(message: Message, state: FSMContext):
    try:
        pill_id = int((message.text or "").strip())
    except ValueError:
        await message.answer("❌ ID должен быть числом.")
        return

    pill_data = await get_pill(message.from_user.id, pill_id)
    if not pill_data:
        await message.answer("❌ Такая таблетка не найдена.")
        return

    pill_name = pill_data[0][1]
    times = [row[2] for row in pill_data if row[2]]
    remove_reminders(pill_id, times)

    if not await delete_pill(message.from_user.id, pill_id):
        await message.answer("❌ Не удалось удалить таблетку.")
        return

    await state.clear()
    await message.answer(f"🗑 Таблетка <b>«{pill_name}»</b> удалена.", parse_mode="HTML", reply_markup=main_menu)


@router.message(lambda message: message.text == "✏️ Изменить расписание")
async def edit_start(message: Message, state: FSMContext):
    await state.clear()
    pills = await get_pills(message.from_user.id)
    if not pills:
        await message.answer("💊 У тебя нет таблеток.", reply_markup=main_menu)
        return

    result = "✏️ <b>Выбери таблетку</b>\n\n"
    current_id = None
    number = 0
    for pill_id, name, time in pills:
        if pill_id != current_id:
            number += 1
            result += f"{number}. {name} — ID: <code>{pill_id}</code>\n"
            current_id = pill_id
    result += "\nВведи ID таблетки:"
    await state.set_state(EditPill.id)
    await message.answer(result, parse_mode="HTML", reply_markup=cancel_menu)


@router.message(EditPill.id)
async def edit_id(message: Message, state: FSMContext):
    try:
        pill_id = int((message.text or "").strip())
    except ValueError:
        await message.answer("❌ ID должен быть числом.")
        return

    pill_data = await get_pill(message.from_user.id, pill_id)
    if not pill_data:
        await message.answer("❌ Такая таблетка не найдена.")
        return

    await state.update_data(pill_id=pill_id)
    await state.set_state(EditPill.times)
    await message.answer(
        f"💊 Таблетка: <b>{pill_data[0][1]}</b>\n\nВведи новое расписание.\n\n"
        "Например:\n<code>08:00 14:00 20:00</code>",
        parse_mode="HTML"
    )


@router.message(EditPill.times)
async def edit_times(message: Message, state: FSMContext):
    times = (message.text or "").split()
    if not validate_times(times):
        await message.answer("❌ Неверный формат времени.\n\nНапример: <code>08:00 14:00 20:00</code>", parse_mode="HTML")
        return

    times = normalize_times(times)
    data = await state.get_data()
    pill_id = data["pill_id"]
    old_pill = await get_pill(message.from_user.id, pill_id)
    if not old_pill:
        await message.answer("❌ Таблетка не найдена.")
        await state.clear()
        return

    pill_name = old_pill[0][1]
    old_times = [row[2] for row in old_pill if row[2]]
    remove_reminders(pill_id, old_times)

    if not await update_schedule(message.from_user.id, pill_id, times):
        await message.answer("❌ Не удалось изменить расписание.")
        return

    for time in times:
        add_reminder(message.bot, pill_id, message.from_user.id, pill_name, time)

    await state.clear()
    await message.answer(
        f"✅ <b>Расписание изменено!</b>\n\n💊 {pill_name}\n🕐 {', '.join(times)}",
        parse_mode="HTML", reply_markup=main_menu
    )


@router.callback_query(lambda callback: callback.data.startswith("pill_taken:"))
async def pill_taken(callback: CallbackQuery):
    try:
        event_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка.", show_alert=True)
        return

    event = await get_dose_event(event_id, callback.from_user.id)
    if not event:
        await callback.answer("❌ Приём не найден.", show_alert=True)
        return

    if event[5] == "taken":
        await callback.answer("Эта таблетка уже отмечена как выпитая.")
        return

    if not await mark_dose_taken(event_id, callback.from_user.id):
        await callback.answer("❌ Не удалось подтвердить приём.", show_alert=True)
        return

    await callback.message.edit_text(
        f"✅ <b>Приём подтверждён</b>\n\n💊 Таблетка: «{event[6]}»",
        parse_mode="HTML"
    )
    await callback.answer("Приём таблетки подтверждён ✅")


@router.callback_query(lambda callback: callback.data.startswith("pill_snooze:"))
async def pill_snooze(callback: CallbackQuery):
    try:
        event_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка.", show_alert=True)
        return

    event = await get_dose_event(event_id, callback.from_user.id)
    if not event:
        await callback.answer("❌ Приём не найден.", show_alert=True)
        return

    if event[5] == "taken":
        await callback.answer("Ты уже подтвердил этот приём.")
        return

    if not await mark_dose_snoozed(event_id, callback.from_user.id):
        await callback.answer("❌ Не удалось отложить напоминание.", show_alert=True)
        return

    schedule_snooze(callback.bot, callback.from_user.id, event_id, event[6])

    await callback.message.edit_text(
        f"⏰ <b>Напоминание отложено на 10 минут.</b>\n\n💊 Таблетка: «{event[6]}»",
        parse_mode="HTML"
    )
    await callback.answer("Напомню через 10 минут ⏰")