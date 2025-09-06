from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import time
from config.middleware import AdminMiddleware
import logging

from feed.models import Place, PlaceCategory, WeekDay

logger = logging.getLogger(__name__)

admin_router = Router()
admin_router.message.middleware(AdminMiddleware())
admin_router.callback_query.middleware(AdminMiddleware())


# Состояния для FSM
class AddPlaceStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_category = State()
    waiting_for_address = State()
    waiting_for_lat = State()
    waiting_for_lon = State()
    waiting_for_opening_time = State()
    waiting_for_closing_time = State()
    waiting_for_working_days = State()
    waiting_for_image_url = State()
    waiting_for_phone = State()
    waiting_for_website = State()
    waiting_for_rating = State()
    waiting_for_price_level = State()
    waiting_for_confirmation = State()  # Новое состояние для подтверждения


# Общая клавиатура с пропуском
skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⏭️ Пропустить")]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Клавиатура подтверждения
confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Сохранить", callback_data="save_place"),
            InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_place")
        ],
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_place")
        ]
    ]
)


@admin_router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Главное меню админ панели"""
    logger.info(f"Admin panel opened by user {message.from_user.id}")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить место")],
            [KeyboardButton(text="📋 Список мест")],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )

    await message.answer("👑 Панель администратора", reply_markup=keyboard)


# Добавление нового места
@admin_router.message(F.text == "➕ Добавить место")
async def start_add_place(message: Message, state: FSMContext):
    """Начало процесса добавления места"""
    logger.info(f"Starting place addition by user {message.from_user.id}")

    await message.answer(
        "Введите название места:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddPlaceStates.waiting_for_name)


# ... [все промежуточные хендлеры остаются прежними до process_price_level] ...

@admin_router.message(AddPlaceStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание места:", reply_markup=skip_keyboard)
    await state.set_state(AddPlaceStates.waiting_for_description)


@admin_router.message(AddPlaceStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    if message.text != "⏭️ Пропустить":
        await state.update_data(description=message.text)

    categories = list(PlaceCategory)
    categories_kb = ReplyKeyboardMarkup(
        keyboard=[
                     [KeyboardButton(text=cat.name) for cat in categories[i:i + 2]]
                     for i in range(0, len(categories), 2)
                 ] + [[KeyboardButton(text="⏭️ Пропустить")]],
        resize_keyboard=True
    )

    await message.answer("Выберите категорию:", reply_markup=categories_kb)
    await state.set_state(AddPlaceStates.waiting_for_category)


@admin_router.message(AddPlaceStates.waiting_for_category)
async def process_category(message: Message, state: FSMContext):
    if message.text != "⏭️ Пропустить":
        valid_categories = [cat.name for cat in PlaceCategory]
        if message.text not in valid_categories:
            await message.answer("❌ Неверная категория! Выберите из списка:")
            return
        await state.update_data(category=message.text)

    await message.answer("Введите адрес места:", reply_markup=skip_keyboard)
    await state.set_state(AddPlaceStates.waiting_for_address)


@admin_router.message(AddPlaceStates.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    if message.text != "⏭️ Пропустить":
        await state.update_data(address=message.text)

    await message.answer("Введите широту (latitude):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddPlaceStates.waiting_for_lat)


@admin_router.message(AddPlaceStates.waiting_for_lat)
async def process_lat(message: Message, state: FSMContext):
    try:
        lat = float(message.text)
        if not (-90 <= lat <= 90):
            await message.answer("❌ Широта должна быть от -90 до 90!")
            return
        await state.update_data(loc_lat=lat)
        await message.answer("Введите долготу (longitude):")
        await state.set_state(AddPlaceStates.waiting_for_lon)
    except ValueError:
        await message.answer("❌ Введите число!")


@admin_router.message(AddPlaceStates.waiting_for_lon)
async def process_lon(message: Message, state: FSMContext):
    try:
        lon = float(message.text)
        if not (-180 <= lon <= 180):
            await message.answer("❌ Долгота должна быть от -180 до 180!")
            return
        await state.update_data(loc_lon=lon)
        await message.answer("Введите время открытия (формат HH:MM):", reply_markup=skip_keyboard)
        await state.set_state(AddPlaceStates.waiting_for_opening_time)
    except ValueError:
        await message.answer("❌ Введите число!")


@admin_router.message(AddPlaceStates.waiting_for_opening_time)
async def process_opening_time(message: Message, state: FSMContext):
    if message.text == "⏭️ Пропустить":
        await state.update_data(opening_time=None)
        await message.answer("Введите время закрытия (формат HH:MM):", reply_markup=skip_keyboard)
        await state.set_state(AddPlaceStates.waiting_for_closing_time)
        return

    try:
        hours, minutes = map(int, message.text.split(':'))
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            await message.answer("❌ Неверное время! Часы: 0-23, минуты: 0-59")
            return
        opening_time = time(hours, minutes)
        await state.update_data(opening_time=opening_time)
        await message.answer("Введите время закрытия (формат HH:MM):", reply_markup=skip_keyboard)
        await state.set_state(AddPlaceStates.waiting_for_closing_time)
    except (ValueError, IndexError):
        await message.answer("❌ Неверный формат времени! Используйте HH:MM")


@admin_router.message(AddPlaceStates.waiting_for_closing_time)
async def process_closing_time(message: Message, state: FSMContext):
    if message.text == "⏭️ Пропустить":
        await state.update_data(closing_time=None)
        # Клавиатура с днями недели
        days_kb = ReplyKeyboardMarkup(
            keyboard=[
                         [KeyboardButton(text=day.name) for day in list(WeekDay)[i:i + 3]]
                         for i in range(0, len(WeekDay), 3)
                     ] + [[KeyboardButton(text="⏭️ Пропустить")]],
            resize_keyboard=True
        )
        await message.answer("Выберите дни работы (через запятую):", reply_markup=days_kb)
        await state.set_state(AddPlaceStates.waiting_for_working_days)
        return

    try:
        hours, minutes = map(int, message.text.split(':'))
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            await message.answer("❌ Неверное время! Часы: 0-23, минуты: 0-59")
            return
        closing_time = time(hours, minutes)
        await state.update_data(closing_time=closing_time)

        # Клавиатура с днями недели
        days_kb = ReplyKeyboardMarkup(
            keyboard=[
                         [KeyboardButton(text=day.name) for day in list(WeekDay)[i:i + 3]]
                         for i in range(0, len(WeekDay), 3)
                     ] + [[KeyboardButton(text="⏭️ Пропустить")]],
            resize_keyboard=True
        )

        await message.answer("Выберите дни работы (через запятую):", reply_markup=days_kb)
        await state.set_state(AddPlaceStates.waiting_for_working_days)
    except (ValueError, IndexError):
        await message.answer("❌ Неверный формат времени! Используйте HH:MM")


@admin_router.message(AddPlaceStates.waiting_for_working_days)
async def process_working_days(message: Message, state: FSMContext):
    if message.text == "⏭️ Пропустить":
        await state.update_data(working_days=[])
        await message.answer("Введите URL изображения:", reply_markup=skip_keyboard)
        await state.set_state(AddPlaceStates.waiting_for_image_url)
        return

    selected_days = [day.strip() for day in message.text.split(',')]
    valid_days = [day.name for day in WeekDay]

    if all(day in valid_days for day in selected_days):
        await state.update_data(working_days=selected_days)
        await message.answer("Введите URL изображения:", reply_markup=skip_keyboard)
        await state.set_state(AddPlaceStates.waiting_for_image_url)
    else:
        await message.answer("❌ Неверные дни недели!")


@admin_router.message(AddPlaceStates.waiting_for_image_url)
async def process_image_url(message: Message, state: FSMContext):
    if message.text != "⏭️ Пропустить":
        # Базовая валидация URL
        if not (message.text.startswith('http://') or message.text.startswith('https://')):
            await message.answer("⚠️ URL должен начинаться с http:// или https://")
        await state.update_data(image_url=message.text)

    await message.answer("Введите телефон:", reply_markup=skip_keyboard)
    await state.set_state(AddPlaceStates.waiting_for_phone)


@admin_router.message(AddPlaceStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    if message.text != "⏭️ Пропустить":
        await state.update_data(phone=message.text)

    await message.answer("Введите сайт:", reply_markup=skip_keyboard)
    await state.set_state(AddPlaceStates.waiting_for_website)


@admin_router.message(AddPlaceStates.waiting_for_website)
async def process_website(message: Message, state: FSMContext):
    if message.text != "⏭️ Пропустить":
        # Базовая валидация URL
        if not (message.text.startswith('http://') or message.text.startswith('https://')):
            await message.answer("⚠️ URL должен начинаться с http:// или https://")
        await state.update_data(website=message.text)

    await message.answer("Введите рейтинг (0-5):", reply_markup=skip_keyboard)
    await state.set_state(AddPlaceStates.waiting_for_rating)


@admin_router.message(AddPlaceStates.waiting_for_rating)
async def process_rating(message: Message, state: FSMContext):
    if message.text == "⏭️ Пропустить":
        await state.update_data(rating=None)
        await message.answer("Введите уровень цен (1-3):", reply_markup=skip_keyboard)
        await state.set_state(AddPlaceStates.waiting_for_price_level)
        return

    try:
        rating = float(message.text)
        if 0 <= rating <= 5:
            await state.update_data(rating=rating)
            await message.answer("Введите уровень цен (1-3):", reply_markup=skip_keyboard)
            await state.set_state(AddPlaceStates.waiting_for_price_level)
        else:
            await message.answer("❌ Рейтинг должен быть от 0 до 5!")
    except ValueError:
        await message.answer("❌ Введите число!")


@admin_router.message(AddPlaceStates.waiting_for_price_level)
async def process_price_level(message: Message, state: FSMContext):
    """Последний шаг - показываем предварительный просмотр"""
    data = await state.get_data()

    if message.text != "⏭️ Пропустить":
        try:
            price_level = int(message.text)
            if 1 <= price_level <= 3:
                data['price_level'] = price_level
                await state.update_data(price_level=price_level)
            else:
                await message.answer("❌ Уровень цен должен быть от 1 до 3!")
                return
        except ValueError:
            await message.answer("❌ Введите число от 1 до 3!")
            return

    # Показываем предварительный просмотр
    await show_place_preview(message, state)


async def show_place_preview(message: Message, state: FSMContext):
    """Показать предварительный просмотр места перед сохранением"""
    data = await state.get_data()

    # Форматируем время
    opening_time = data.get('opening_time')
    closing_time = data.get('closing_time')
    time_str = "Не указано"
    if opening_time and closing_time:
        time_str = f"{opening_time.strftime('%H:%M')} - {closing_time.strftime('%H:%M')}"
    elif opening_time:
        time_str = f"с {opening_time.strftime('%H:%M')}"
    elif closing_time:
        time_str = f"до {closing_time.strftime('%H:%M')}"

    # Форматируем дни работы
    working_days = data.get('working_days', [])
    days_str = ", ".join(working_days) if working_days else "Не указаны"

    # Форматируем уровень цен
    price_level = data.get('price_level')
    price_str = {1: "$ (Низкий)", 2: "$$ (Средний)", 3: "$$$ (Высокий)"}.get(price_level, "Не указан")

    preview_text = f"""
📍 **Предварительный просмотр места:**

🏷️ **Название:** {data.get('name', 'Не указано')}
📝 **Описание:** {data.get('description', 'Не указано')}
🏢 **Категория:** {data.get('category', 'Не указана')}
📍 **Адрес:** {data.get('address', 'Не указан')}
🗺️ **Координаты:** {data.get('loc_lat', 'N/A')}, {data.get('loc_lon', 'N/A')}
⏰ **Время работы:** {time_str}
📅 **Дни работы:** {days_str}
🖼️ **Изображение:** {'Добавлено' if data.get('image_url') else 'Не добавлено'}
📞 **Телефон:** {data.get('phone', 'Не указан')}
🌐 **Сайт:** {data.get('website', 'Не указан')}
⭐ **Рейтинг:** {data.get('rating', 'Не указан')}
💰 **Уровень цен:** {price_str}
    """

    await message.answer(
        preview_text,
        reply_markup=confirmation_keyboard,
        parse_mode="Markdown"
    )
    await state.set_state(AddPlaceStates.waiting_for_confirmation)


@admin_router.callback_query(F.data == "save_place", AddPlaceStates.waiting_for_confirmation)
async def save_place_confirm(callback, state: FSMContext, session: AsyncSession):
    """Сохранение места в базу данных"""
    try:
        data = await state.get_data()

        logger.info(f"Saving place by admin {callback.from_user.id}: {data.get('name')}")

        # Создаем новое место
        new_place = Place(
            name=data['name'],
            description=data.get('description'),
            category=data.get('category'),
            address=data.get('address'),
            loc_lat=data['loc_lat'],
            loc_lon=data['loc_lon'],
            opening_time=data.get('opening_time'),
            closing_time=data.get('closing_time'),
            working_days=data.get('working_days', []),
            image_url=data.get('image_url'),
            phone=data.get('phone'),
            website=data.get('website'),
            rating=data.get('rating'),
            price_level=data.get('price_level')
        )

        session.add(new_place)
        await session.commit()

        logger.info(f"Place '{data.get('name')}' successfully saved by admin {callback.from_user.id}")

        await callback.message.edit_text(
            "✅ Место успешно добавлено!",
            reply_markup=None
        )
        await callback.message.answer(
            "Вы можете добавить еще одно место или вернуться в главное меню",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="➕ Добавить место")],
                    [KeyboardButton(text="👑 Админ панель")],
                    [KeyboardButton(text="❌ Отмена")]
                ],
                resize_keyboard=True
            )
        )
        await state.clear()

    except Exception as e:
        logger.error(f"Error saving place by admin {callback.from_user.id}: {e}")
        await session.rollback()
        await callback.message.edit_text(
            f"❌ Ошибка при сохранении места: {str(e)}",
            reply_markup=None
        )
        await state.clear()

    await callback.answer()


@admin_router.callback_query(F.data == "edit_place", AddPlaceStates.waiting_for_confirmation)
async def edit_place_confirm(callback, state: FSMContext):
    """Вернуться к редактированию места"""
    await callback.message.edit_text(
        "Редактирование пока не реализовано. Начните заново.",
        reply_markup=None
    )
    await callback.message.answer(
        "Введите название места:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddPlaceStates.waiting_for_name)
    await callback.answer()


@admin_router.callback_query(F.data == "cancel_place", AddPlaceStates.waiting_for_confirmation)
async def cancel_place_confirm(callback, state: FSMContext):
    """Отмена добавления места"""
    logger.info(f"Place addition cancelled by admin {callback.from_user.id}")

    await callback.message.edit_text("❌ Добавление места отменено", reply_markup=None)
    await state.clear()
    await callback.answer()


# Отмена операции
@admin_router.message(Command("cancel"))
@admin_router.message(F.text == "❌ Отмена")
async def cancel_operation(message: Message, state: FSMContext):
    """Общая отмена операции"""
    await state.clear()
    await message.answer("Операция отменена", reply_markup=ReplyKeyboardRemove())


# Дополнительная команда для списка мест (пример)
@admin_router.message(F.text == "📋 Список мест")
async def list_places(message: Message, session: AsyncSession):
    """Показать список всех мест"""
    from sqlalchemy import select

    result = await session.execute(select(Place).limit(10))
    places = result.scalars().all()

    if not places:
        await message.answer("📋 Список мест пуст")
        return

    places_text = "📋 **Список мест:**\n\n"
    for i, place in enumerate(places, 1):
        places_text += f"{i}. **{place.name}**\n"
        places_text += f"   📍 {place.address or 'Адрес не указан'}\n"
        places_text += f"   🏢 {place.category or 'Категория не указана'}\n\n"

    await message.answer(places_text, parse_mode="Markdown")