from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database import add_user, get_all_users_morning
from datetime import datetime
import os
from dotenv import load_dotenv # type: ignore
from getWeather import getWeatherToday
import locale
from keyboards import main_menu
from states import *
from morning import morning_title

from scheduler import add_morning_information_job

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

load_dotenv()

router = Router()

VERSION = os.getenv("VERSION")


@router.message(Command("start"))
async def start(message: Message):
    await add_user(
        user_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username,
        is_premium=bool(message.from_user.is_premium)
    )

    await add_morning_information_job(
        bot=message.bot,
        user_id=message.from_user.id,
        first_name=message.from_user.first_name,
        time='8:30'
    )

    await message.answer(
        f"💊 <b>Салют, {message.from_user.first_name}!</b>\n\nБот разработан на aiogram3.0 + chatGPT\n\n<a link='t.me/xae6ka'>За более подробной информацией обращаться к единственному разрабочику, тык\n\nVersion: {VERSION}</a>",
        parse_mode="HTML",
        reply_markup=main_menu
    )


@router.message(lambda message: message.text == "🛠 О разработчике")
async def about_me(message: Message, state: FSMContext):
    await message.answer("Полным владельцем данного кода и бота является <a href='t.me/xae6ka'>Мамкин Программист</a>, нужен сайт, телеграмм-бот, либо дизайн любой сложности - тебе сюда. Предложение пока находиться на тестовой ветке разработки.\n\n<b>Каналы:</b>\n\n<a href='t.me/xae6kaa_room'>Комната Мамкиного Программиста</a> | <a href='t.me/xae6ka_room'>Комната Мамкиного Дизайнера</a>", parse_mode='HTML')


@router.message(lambda message: message.text == "📚 Основная информация" or message.text == "📱 На главную")
async def add_start(message: Message, state: FSMContext):
    weather = getWeatherToday()

    await message.answer(f'{await morning_title(weather, message.from_user.first_name, message.from_user.id)}', parse_mode="HTML", reply_markup=main_menu)


@router.message(lambda message: message.text == "❌ Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Действие отменено.", reply_markup=main_menu)
