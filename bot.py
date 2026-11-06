import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import init_db
from handlers.handlers import router
from scheduler import (
    start_scheduler,
    load_schedules,
    load_active_events,
    restore_morning_jobs
)


from handlers.broadcast_handlers import router as broadcast_router
from handlers.admin_handlers import router as admin_router
from handlers.pills_handlers import router as pills_router
from handlers.tasks_handlers import router as tasks_router
from handlers.settins_handlers import router as settins_handlers

async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    dp.include_router(admin_router)
    dp.include_router(pills_router)
    dp.include_router(tasks_router)
    dp.include_router(broadcast_router)
    dp.include_router(settins_handlers)

    start_scheduler()
    await load_schedules(bot)
    await load_active_events(bot)
    await restore_morning_jobs(bot)

    print("🤖 Telegram-бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
