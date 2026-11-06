from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards import settings_menu, morning_menu, cancel_menu

from states import ChangeTime

from scheduler import add_morning_information_job
from database import get_all_users_morning

router = Router()

@router.message(lambda message: message.text == "⚙️ Настройки" or message.text == "⭕️ Назад")
async def settings(message: Message, state: FSMContext):
    await message.answer(f'⚙️ Меню настроек', parse_mode="HTML", reply_markup=settings_menu)

@router.message(lambda message: message.text == "🌇 Утренняя рассылка")
async def settings(message: Message, state: FSMContext):
    await message.answer(f'🌇 | Меню настройки утренней рассылки', parse_mode="HTML", reply_markup=morning_menu)



@router.message(lambda message: message.text == "📊 Изменить время отправки сообщения")
async def change_time(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ChangeTime.time)
    await message.answer("🌇 | Введи время, в которое отправлять рассылку\n\nВремя отправлять в формате <code>8:30 10:15  и т.д.</code>", parse_mode='HTML', reply_markup=cancel_menu)


@router.message(ChangeTime.time)
async def change_time(message: Message, state: FSMContext):
    time = (message.text or "").strip()
    hour, minute = map(int, time.split(':'))

    if hour > 24 or hour < 0 or minute > 60 or minute < 0:
        await message.answer(
                f"🔴 Данные введены некорректно!", reply_markup=settings_menu
            )
        return

    await add_morning_information_job(
            bot=message.bot,
            user_id=message.from_user.id,
            first_name=message.from_user.first_name,
            time=time
    )

    await message.answer(
        f"🌇 | Время изменено на {time}", reply_markup=settings_menu
    )

    await state.clear()