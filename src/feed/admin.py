from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import time

from feed.models import Place, PlaceCategory, WeekDay

admin_router = Router()


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


# Общая клавиатура с пропуском
skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⏭️ Пропустить")]],
    resize_keyboard=True,
    one_time_keyboard=True
)


# Команда для входа в админку
@admin_router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id != 2084948859:
        await message.answer("❌ Доступ запрещен")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить место")],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )

    await message.answer("👑 Панель администратора", reply_markup=keyboard)


# Добавление нового места
@admin_router.message(F.text == "➕ Добавить место")
async def start_add_place(message: Message, state: FSMContext):
    if message.from_user.id != 2084948859:
        return

    await message.answer(
        "Введите название места:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddPlaceStates.waiting_for_name)


@admin_router.message(AddPlaceStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    if message.from_user.id != 2084948859:
        return

    await state.update_data(name=message.text)
    await message.answer("Введите описание места:", reply_markup=skip_keyboard)
    await state.set_state(AddPlaceStates.waiting_for_description)


@admin_router.message(AddPlaceStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    if message.from_user.id != 2084948859:
        return

    if message.text != "⏭️ Пропустить":
        await state.update_data(description=message.text)

    # Клавиатура с категориями
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
    if message.from_user.id != 2084948859:
        return

    if message.text != "⏭️ Пропустить":
        # Проверяем, что выбранная категория существует в enum
        valid_categories = [cat.name for cat in PlaceCategory]
        if message.text not in valid_categories:
            await message.answer("❌ Неверная категория! Выберите из списка:")
            return
        await state.update_data(category=message.text)

    await message.answer("Введите адрес места:", reply_markup=skip_keyboard)
    await state.set_state(AddPlaceStates.waiting_for_address)


@admin_router.message(AddPlaceStates.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    if message.from_user.id != 2084948859:
        return

    if message.text != "⏭️ Пропустить":
        await state.update_data(address=message.text)

    await message.answer("Введите широту (latitude):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddPlaceStates.waiting_for_lat)


@admin_router.message(AddPlaceStates.waiting_for_lat)
async def process_lat(message: Message, state: FSMContext):
    if message.from_user.id != 2084948859:
        return

    try:
        lat = float(message.text)
        await state.update_data(loc_lat=lat)
        await message.answer("Введите долготу (longitude):")
        await state.set_state(AddPlaceStates.waiting_for_lon)
    except ValueError:
        await message.answer("❌ Введите число!")


@admin_router.message(AddPlaceStates.waiting_for_lon)
async def process_lon(message: Message, state: FSMContext):
    if message.from_user.id != 2084948859:
        return

    try:
        lon = float(message.text)
        await state.update_data(loc_lon=lon)
        await message.answer("Введите время открытия (формат HH:MM):", reply_markup=skip_keyboard)
        await state.set_state(AddPlaceStates.waiting_for_opening_time)
    except ValueError:
        await message.answer("❌ Введите число!")


@admin_router.message(AddPlaceStates.waiting_for_opening_time)
async def process_opening_time(message: Message, state: FSMContext):
    if message.from_user.id != 2084948859:
        return

    if message.text == "⏭️ Пропустить":
        await state.update_data(opening_time=None)
        await message.answer("Введите время закрытия (формат HH:MM):", reply_markup=skip_keyboard)
        await state.set_state(AddPlaceStates.waiting_for_closing_time)
        return

    try:
        hours, minutes = map(int, message.text.split(':'))
        opening_time = time(hours, minutes)
        await state.update_data(opening_time=opening_time)
        await message.answer("Введите время закрытия (формат HH:MM):", reply_markup=skip_keyboard)
        await state.set_state(AddPlaceStates.waiting_for_closing_time)
    except:
        await message.answer("❌ Неверный формат времени!")


@admin_router.message(AddPlaceStates.waiting_for_closing_time)
async def process_closing_time(message: Message, state: FSMContext):
    if message.from_user.id != 2084948859:
        return

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
    except:
        await message.answer("❌ Неверный формат времени!")


@admin_router.message(AddPlaceStates.waiting_for_working_days)
async def process_working_days(message: Message, state: FSMContext):
    if message.from_user.id != 2084948859:
        return

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
    if message.from_user.id != 2084948859:
        return

    if message.text != "⏭️ Пропустить":
        await state.update_data(image_url=message.text)

    await message.answer("Введите телефон:", reply_markup=skip_keyboard)
    await state.set_state(AddPlaceStates.waiting_for_phone)


@admin_router.message(AddPlaceStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    if message.from_user.id != 2084948859:
        return

    if message.text != "⏭️ Пропустить":
        await state.update_data(phone=message.text)

    await message.answer("Введите сайт:", reply_markup=skip_keyboard)
    await state.set_state(AddPlaceStates.waiting_for_website)


@admin_router.message(AddPlaceStates.waiting_for_website)
async def process_website(message: Message, state: FSMContext):
    if message.from_user.id != 2084948859:
        return

    if message.text != "⏭️ Пропустить":
        await state.update_data(website=message.text)

    await message.answer("Введите рейтинг (0-5):", reply_markup=skip_keyboard)
    await state.set_state(AddPlaceStates.waiting_for_rating)


@admin_router.message(AddPlaceStates.waiting_for_rating)
async def process_rating(message: Message, state: FSMContext):
    if message.from_user.id != 2084948859:
        return

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
async def process_price_level(message: Message, state: FSMContext, session: AsyncSession):
    if message.from_user.id != 2084948859:
        return

    data = await state.get_data()

    if message.text != "⏭️ Пропустить":
        try:
            price_level = int(message.text)
            if 1 <= price_level <= 3:
                data['price_level'] = price_level
        except ValueError:
            await message.answer("❌ Введите число от 1 до 3!")
            return

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

    await message.answer("✅ Место успешно добавлено!", reply_markup=ReplyKeyboardRemove())
    await state.clear()


# Отмена операции
@admin_router.message(Command("cancel"))
@admin_router.message(F.text == "❌ Отмена")
async def cancel_operation(message: Message, state: FSMContext):
    if message.from_user.id != 2084948859:
        return

    await state.clear()
    await message.answer("Операция отменена", reply_markup=ReplyKeyboardRemove())