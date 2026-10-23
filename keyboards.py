from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Основная информация")],
        [KeyboardButton(text="➕ Задачи"), KeyboardButton(text="💊 Таблетки")],
        [KeyboardButton(text="🛠 О разработчике")]
    ],
    resize_keyboard=True
)


pills_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 На главную")],
        [KeyboardButton(text="➕ Добавить таблетку"), KeyboardButton(text="💊 Мои таблетки")],
        [KeyboardButton(text="✏️ Изменить расписание"), KeyboardButton(text="🗑 Удалить таблетку")]
    ],
    resize_keyboard=True
)

tasks_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 На главную")],
        [KeyboardButton(text="📌 Мои задачи")],
        [KeyboardButton(text="✏️ Добавить задачу"), KeyboardButton(text="🗑 Удалить задачу")]
    ],
    resize_keyboard=True
)


cancel_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True
)