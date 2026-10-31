import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import init_db
from handlers import router
from scheduler import (
    start_scheduler,
    load_schedules,
    load_active_events,
    add_morning_information_job
)
from broadcast import router as broadcast_router


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    dp.include_router(broadcast_router)

    start_scheduler()
    await load_schedules(bot)
    await load_active_events(bot)
    add_morning_information_job(bot)

    print("🤖 Telegram-бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
