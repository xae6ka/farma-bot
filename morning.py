from database import get_all_users
from getWeather import getWeatherToday

from datetime import datetime

from database import get_tasks

from classes import Task

async def my_tasks(user_id):
    data = await get_tasks(user_id)

    text = "\n\n<b>📝 | Мои задачи на ближайшее время:</b>\n\n"
        
    if len(data) > 0:
        task_list = []
            
        for el in data:
            task_list.append(Task(*el))
    
        for el in sorted(task_list, key=lambda el: el.deadline - datetime.now()):
            text += '\t' + el.getTask() + '\n'
    else:
        text += 'Список задач пуст'

    return text


async def morning_title(weather, first_name, user_id):
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
    Вероятность дождя: {weather['PrePercent']}%, суммарно будет идти {weather['preHours']} часов."""

    text += await my_tasks(user_id)

    return text


async def send_morning_information(bot):
    users = await get_all_users()

    weather = getWeatherToday()

    for user_id, first_name in users:
        text = morning_title(weather, first_name, user_id)

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