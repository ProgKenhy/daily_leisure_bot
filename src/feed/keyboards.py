from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton

from feed.models import WeekDay, PlaceCategory

main_admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить место")],
        [KeyboardButton(text="📋 Список мест")],
        [KeyboardButton(text="✏️ Редактировать место")],
        [KeyboardButton(text="❌ Отмена")]
    ],
    resize_keyboard=True
)
name_keyboard = reply_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️ Редактировать существующее")],
        [KeyboardButton(text="➕ Создать новое с этим названием")],
        [KeyboardButton(text="🔁 Изменить название")]
    ],
    resize_keyboard=True
)

skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⏭️ Пропустить")]],
    resize_keyboard=True,
    one_time_keyboard=True
)

days_kb = ReplyKeyboardMarkup(
    keyboard=[
                 [KeyboardButton(text=day.name) for day in list(WeekDay)[i:i + 3]]
                 for i in range(0, len(WeekDay), 3)
             ] + [[KeyboardButton(text="⏭️ Пропустить")]],
    resize_keyboard=True
)

categories = list(PlaceCategory)
categories_kb = ReplyKeyboardMarkup(
    keyboard=[
                 [KeyboardButton(text=cat.name) for cat in categories[i:i + 2]]
                 for i in range(0, len(categories), 2)
             ] + [[KeyboardButton(text="⏭️ Пропустить")]],
    resize_keyboard=True
)

edit_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️ Редактировать место")],
        [KeyboardButton(text="👑 Админ панель")]
    ],
    resize_keyboard=True
)


def get_confirmation_keyboard(existing_place_id=None):
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Сохранить", callback_data="save_place"),
            InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_place")
        ]
    ]

    if existing_place_id:
        keyboard.append([
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_place_{existing_place_id}")
        ])

    keyboard.append([
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_place")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)