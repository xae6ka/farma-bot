from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import get_or_create_dose_event, get_active_dose_events, get_dose_event
from morning import send_morning_information

scheduler = AsyncIOScheduler()


def get_pill_keyboard(event_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Выпил", callback_data=f"pill_taken:{event_id}"),
        InlineKeyboardButton(text="⏰ Через 10 минут", callback_data=f"pill_snooze:{event_id}")
    ]])


def add_morning_information_job(bot):
    scheduler.add_job(
        send_morning_information,
        trigger="cron",
        hour=8,
        minute=30,
        args=[bot],
        id="morning_information",
        replace_existing=True
    )

    print("🌅 Утренняя рассылка запланирована на 08:30")


async def remind_5_minutes(bot, user_id: int, pill_name: str):
    await bot.send_message(
        user_id,
        f"💊 Через 5 минут нужно выпить таблетку «{pill_name}»."
    )


async def remind_now(bot, user_id: int, pill_id: int, pill_name: str, time_str: str):
    scheduled_date = datetime.now().strftime("%Y-%m-%d")
    event_id, status = await get_or_create_dose_event(
        pill_id, user_id, scheduled_date, time_str
    )

    if status == "taken":
        return

    await bot.send_message(
        user_id,
        f"💊 Тебе нужно выпить таблетку «{pill_name}» сейчас.",
        reply_markup=get_pill_keyboard(event_id)
    )


async def remind_snoozed(bot, user_id: int, event_id: int, pill_name: str):
    event = await get_dose_event(event_id, user_id)
    if not event or event[5] == "taken":
        return

    await bot.send_message(
        user_id,
        f"⏰ Ты ещё не подтвердил приём таблетки «{pill_name}».",
        reply_markup=get_pill_keyboard(event_id)
    )


def schedule_snooze(bot, user_id: int, event_id: int, pill_name: str):
    scheduler.add_job(
        remind_snoozed,
        trigger="date",
        run_date=datetime.now() + timedelta(minutes=10),
        args=[bot, user_id, event_id, pill_name],
        id=f"snooze_{event_id}",
        replace_existing=True
    )


def get_now_job_id(pill_id: int, time_str: str):
    return f"pill_now_{pill_id}_{time_str.replace(':', '_')}"


def get_before_job_id(pill_id: int, time_str: str):
    return f"pill_before_{pill_id}_{time_str.replace(':', '_')}"


def add_reminder(bot, pill_id: int, user_id: int, pill_name: str, time_str: str):
    hour, minute = map(int, time_str.split(":"))

    scheduler.add_job(
        remind_now,
        trigger="cron",
        hour=hour,
        minute=minute,
        args=[bot, user_id, pill_id, pill_name, time_str],
        id=get_now_job_id(pill_id, time_str),
        replace_existing=True
    )

    before = datetime.now().replace(
        hour=hour, minute=minute, second=0, microsecond=0
    ) - timedelta(minutes=5)

    scheduler.add_job(
        remind_5_minutes,
        trigger="cron",
        hour=before.hour,
        minute=before.minute,
        args=[bot, user_id, pill_name],
        id=get_before_job_id(pill_id, time_str),
        replace_existing=True
    )


def remove_reminders(pill_id: int, times: list[str]):
    for time_str in times:
        for job_id in (
            get_now_job_id(pill_id, time_str),
            get_before_job_id(pill_id, time_str),
        ):
            try:
                scheduler.remove_job(job_id)
            except Exception:
                pass


def start_scheduler():
    scheduler.start()


async def load_schedules(bot):
    from database import get_all_schedules
    for pill_id, user_id, pill_name, schedule_id, time_str in await get_all_schedules():
        add_reminder(bot, pill_id, user_id, pill_name, time_str)


async def load_active_events(bot):
    now = datetime.now()
    for event_id, pill_id, user_id, scheduled_date, scheduled_time, status, pill_name in await get_active_dose_events():
        if status != "snoozed":
            continue

        scheduler.add_job(
            remind_snoozed,
            trigger="date",
            run_date=now + timedelta(minutes=1),
            args=[bot, user_id, event_id, pill_name],
            id=f"snooze_{event_id}",
            replace_existing=True
        )
