from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


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

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 На главную")],
        [KeyboardButton(text="🗒 Отчет")],
        [KeyboardButton(text="Null"), KeyboardButton(text="🔗 Рассылка")],
    ],
    resize_keyboard=True
)

#это пиздец
def broadcast_photo_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="⏭ Пропустить",
        callback_data="broadcast_skip_photo"
    )

    return builder.as_markup()


def broadcast_confirm_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Отправить всем",
        callback_data="broadcast_confirm"
    )

    builder.button(
        text="❌ Отменить",
        callback_data="broadcast_cancel"
    )

    builder.adjust(1)

    return builder.as_markup()