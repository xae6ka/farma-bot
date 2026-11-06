
import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramRetryAfter

from states import BroadcastStates
from keyboards import (
    broadcast_photo_keyboard,
    broadcast_confirm_keyboard
)

from database import get_all_users, is_admin


router = Router()


# Проверка администратора
async def check_admin(user_id: int) -> bool:
    return bool(await is_admin(user_id))


# Отправка с повтором при ограничении Telegram
async def send_with_retry(method, **kwargs):
    while True:
        try:
            return await method(**kwargs)

        except TelegramRetryAfter as error:
            await asyncio.sleep(error.retry_after + 1)


# Начало рассылки через обычную кнопку
@router.message(F.text == "🔗 Рассылка")
async def start_broadcast(message: Message, state: FSMContext):

    if not await check_admin(message.from_user.id):
        await message.answer("❌ Нет доступа")
        return

    await state.clear()
    await state.set_state(BroadcastStates.waiting_photo)

    await message.answer(
        "📨 <b>Создание рассылки</b>\n\n"
        "Отправь фотографию или пропусти этот шаг.",
        reply_markup=broadcast_photo_keyboard(),
        parse_mode="HTML"
    )


# Пропуск фотографии
@router.callback_query(
    BroadcastStates.waiting_photo,
    F.data == "broadcast_skip_photo"
)
async def skip_photo(callback: CallbackQuery, state: FSMContext):

    if not await check_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await state.update_data(photo=None)
    await state.set_state(BroadcastStates.waiting_text)

    await callback.message.edit_text(
        "✏️ Теперь отправь текст рассылки.\n\n"
        "Поддерживается HTML-разметка."
    )

    await callback.answer()


# Получение фотографии
@router.message(BroadcastStates.waiting_photo, F.photo)
async def receive_photo(message: Message, state: FSMContext):

    if not await check_admin(message.from_user.id):
        return

    photo = message.photo[-1].file_id

    await state.update_data(photo=photo)
    await state.set_state(BroadcastStates.waiting_text)

    await message.answer(
        "✅ Фотография сохранена.\n\n"
        "Теперь отправь текст рассылки в формате HTML."
    )


# Получение текста
@router.message(BroadcastStates.waiting_text, F.text)
async def receive_text(message: Message, state: FSMContext):

    if not await check_admin(message.from_user.id):
        return

    text = message.text

    await state.update_data(text=text)
    data = await state.get_data()

    users = await get_all_users()

    await state.set_state(BroadcastStates.confirmation)

    # Предпросмотр фотографии
    if data.get("photo"):
        await message.answer_photo(
            photo=data["photo"],
            caption="📷 Предпросмотр фотографии"
        )

    # Предпросмотр текста
    await message.answer(
        "📨 <b>Предпросмотр рассылки</b>\n\n"
        f"{text}\n\n"
        f"👥 Получателей: {len(users)}",
        parse_mode="HTML",
        reply_markup=broadcast_confirm_keyboard()
    )


# Подтверждение рассылки
@router.callback_query(
    BroadcastStates.confirmation,
    F.data == "broadcast_confirm"
)
async def confirm_broadcast(
    callback: CallbackQuery,
    state: FSMContext
):

    if not await check_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    data = await state.get_data()

    photo = data.get("photo")
    text = data.get("text")

    if not text:
        await callback.answer("Текст рассылки отсутствует!", show_alert=True)
        return

    await state.clear()

    await callback.message.edit_text("⏳ Рассылка запущена...")
    await callback.answer()

    users = await get_all_users()

    success = 0
    failed = 0

    for user in users:
        user_id = user[0]

        try:
            # Отправляем фотографию
            if photo:
                await send_with_retry(
                    callback.bot.send_photo,
                    chat_id=user_id,
                    photo=photo
                )

            # Отправляем HTML-текст
            await send_with_retry(
                callback.bot.send_message,
                chat_id=user_id,
                text=text,
                parse_mode="HTML"
            )

            success += 1

        except Exception as error:
            failed += 1
            print(f"Ошибка отправки пользователю {user_id}: {error}")

        await asyncio.sleep(0.05)

    # Отчёт
    await callback.message.answer(
        "✅ <b>Рассылка завершена!</b>\n\n"
        f"👥 Всего получателей: {len(users)}\n"
        f"🟢 Успешно: {success}\n"
        f"🔴 Ошибки: {failed}",
        parse_mode="HTML"
    )


# Отмена рассылки
@router.callback_query(
    BroadcastStates.confirmation,
    F.data == "broadcast_cancel"
)
async def cancel_broadcast(
    callback: CallbackQuery,
    state: FSMContext
):

    if not await check_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await state.clear()

    await callback.message.edit_text(
        "❌ Рассылка отменена."
    )

    await callback.answer()
