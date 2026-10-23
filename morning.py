from database import get_all_users
from getWeather import getWeatherToday


async def send_morning_information(bot):

    users = await get_all_users()

    weather = getWeatherToday()

    for user_id, first_name in users:

        text = f"""
<b>🌅 | Доброе утро, {first_name}!</b>

Город: Санкт-Петербург
Дата: {weather['today']}
День недели: {weather['dayNum']}
Взять зонт: {weather['getUmbrella']}

<b>☀️ | Погода на сегодня:</b>

Температура: {weather['minTemp']} - {weather['maxTemp']}°C
Ощущается как: {weather['minTempO']} - {weather['maxTempO']}°C
Максимальная скорость ветра: {weather['wind']} м/с
Продолжительность светового дня: {weather['dayling']} часов
Вероятность дождя: {weather['PrePercent']}%, суммарно будет идти {weather['preHours']} часов.

<b>📝 | Мои задачи на ближайшее время:</b>

Хуй
"""

        try:
            await bot.send_message(
                user_id,
                text,
                parse_mode="HTML"
            )
        except Exception as e:
            print(
                f"Не удалось отправить сообщение "
                f"{user_id}: {e}"
            )