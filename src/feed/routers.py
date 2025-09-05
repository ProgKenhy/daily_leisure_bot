# from aiogram import Router, F
# from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
# from aiogram.filters import Command
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, func
# from datetime import datetime, time
#
# from users.models import User, UserPlaceHistory, UserFeedState
# from feed.models import Place
#
# feed_router = Router()
#
#
# async def get_or_create_feed_state(session: AsyncSession, user_id: int) -> UserFeedState:
#     """Получаем или создаем состояние ленты пользователя"""
#     stmt = select(UserFeedState).where(UserFeedState.user_id == user_id)
#     result = await session.execute(stmt)
#     state = result.scalar_one_or_none()
#
#     if not state:
#         state = UserFeedState(user_id=user_id)
#         session.add(state)
#         await session.commit()
#
#     return state
#
#
# async def get_place_history(session: AsyncSession, user_id: int, place_id: int) -> UserPlaceHistory:
#     """Получаем историю взаимодействия с местом"""
#     stmt = select(UserPlaceHistory).where(
#         UserPlaceHistory.user_id == user_id,
#         UserPlaceHistory.place_id == place_id
#     )
#     result = await session.execute(stmt)
#     return result.scalar_one_or_none()
#
#
# async def update_place_history(session: AsyncSession, user_id: int, place_id: int, **kwargs):
#     """Обновляем историю показа места"""
#     history = await get_place_history(session, user_id, place_id)
#
#     if not history:
#         history = UserPlaceHistory(user_id=user_id, place_id=place_id)
#         session.add(history)
#
#     for key, value in kwargs.items():
#         if hasattr(history, key):
#             if key == 'show_count':
#                 setattr(history, key, getattr(history, key) + value)
#             else:
#                 setattr(history, key, value)
#
#     history.last_shown = datetime.now()
#     await session.commit()
#     return history
#
#
# @feed_router.message(Command(commands='feed'))
# async def cmd_feed(message: Message, session: AsyncSession):
#     keyboard = ReplyKeyboardMarkup(
#         keyboard=[
#             [KeyboardButton(text="Настолки"), KeyboardButton(text="Мероприятия")],
#             [KeyboardButton(text="Места")]
#         ],
#         resize_keyboard=True,
#         one_time_keyboard=True
#     )
#     await message.answer(
#         "Выбери сферу, которая тебя сегодня интересует.",
#         reply_markup=keyboard
#     )
#
#
# @feed_router.message(F.text == "Места")
# async def handle_places(message: Message, session: AsyncSession):
#     user_id = message.from_user.id
#
#     # Сбрасываем состояние ленты
#     feed_state = await get_or_create_feed_state(session, user_id)
#     feed_state.last_place_id = None
#     await session.commit()
#
#     # Показываем первое место
#     await show_next_place(message, session)
#
#
# async def show_next_place(message: Message, session: AsyncSession):
#     user_id = message.from_user.id
#
#     # Получаем состояние пользователя
#     user_stmt = select(User).where(User.tg_id == user_id)
#     user_result = await session.execute(user_stmt)
#     user = user_result.scalar_one_or_none()
#
#     if not user or not user.loc_lat or not user.loc_lon:
#         await message.answer(
#             "📍 Сначала укажи свое местоположение через /start",
#             reply_markup=ReplyKeyboardRemove()
#         )
#         return
#
#     # Получаем следующее место с учетом истории
#     place = await get_next_place_for_user(session, user_id, user.loc_lat, user.loc_lon)
#
#     if not place:
#         await message.answer("😔 Нет подходящих мест рядом. Попробуй позже.")
#         return
#
#     # Обновляем историю показа
#     await update_place_history(session, user_id, place.id, show_count=1)
#
#     # Обновляем состояние ленты
#     feed_state = await get_or_create_feed_state(session, user_id)
#     feed_state.last_place_id = place.id
#     await session.commit()
#
#     # Формируем сообщение
#     caption = f"🏛️ {place.name}\n\n{place.description or 'Описание отсутствует'}\n\n"
#
#     if place.address:
#         caption += f"📍 Адрес: {place.address}\n"
#
#     is_open = await check_if_place_open(place)
#     status = "🟢 Открыто" if is_open else "🔴 Закрыто"
#     caption += f"🕒 {status}\n"
#
#     if place.rating and place.rating > 0:
#         caption += f"⭐ Рейтинг: {place.rating}/5.0\n"
#
#     if place.price_level:
#         price_map = {1: "💰 Недорого", 2: "💰💰 Средние цены", 3: "💰💰💰 Дорого"}
#         caption += f"{price_map.get(place.price_level, '💰 Цены не указаны')}\n"
#
#     # Клавиатура для навигации
#     keyboard = ReplyKeyboardMarkup(
#         keyboard=[
#             [KeyboardButton(text="➡️ Следующее место"), KeyboardButton(text="❤️ Лайк")],
#             [KeyboardButton(text="👎 Дизлайк"), KeyboardButton(text="📌 Сохранить")],
#             [KeyboardButton(text="🎯 Выбрать категорию"), KeyboardButton(text="🗺️ Обновить локацию")]
#         ],
#         resize_keyboard=True
#     )
#
#     # Отправляем фото места или текст
#     if place.image_url:
#         await message.answer_photo(
#             photo=place.image_url,
#             caption=caption,
#             reply_markup=keyboard
#         )
#     else:
#         await message.answer(
#             text=caption,
#             reply_markup=keyboard
#         )
#
#
# async def get_next_place_for_user(session: AsyncSession, user_id: int, user_lat: float, user_lon: float):
#     """Получаем следующее место для пользователя с учетом истории"""
#     # Подзапрос для получения количества показов каждого места
#     show_count_subquery = (
#         select(
#             UserPlaceHistory.place_id,
#             func.coalesce(func.sum(UserPlaceHistory.show_count), 0).label('total_shows')
#         )
#         .where(UserPlaceHistory.user_id == user_id)
#         .group_by(UserPlaceHistory.place_id)
#         .subquery()
#     )
#
#     # Основной запрос с сортировкой по количеству показов и расстоянию
#     stmt = (
#         select(Place, show_count_subquery.c.total_shows)
#         .outerjoin(show_count_subquery, Place.id == show_count_subquery.c.place_id)
#         .where(Place.is_active == True)
#         .order_by(
#             show_count_subquery.c.total_shows.asc(),  # Сначала места с наименьшим количеством показов
#             func.abs(Place.loc_lat - user_lat) + func.abs(Place.loc_lon - user_lon)  # Затем по расстоянию
#         )
#         .limit(1)
#     )
#
#     result = await session.execute(stmt)
#     row = result.first()
#
#     return row[0] if row else None
#
#
# async def check_if_place_open(place: Place) -> bool:
#     """Проверяем, открыто ли место в текущее время"""
#     if not place.opening_time or not place.closing_time or not place.working_days:
#         return True
#
#     now = datetime.now()
#     current_time = now.time()
#     current_weekday = now.strftime("%A").lower()
#
#     if current_weekday not in [day.value for day in place.working_days]:
#         return False
#
#     return place.opening_time <= current_time <= place.closing_time
#
#
# # Обработчики действий
# @feed_router.message(F.text == "➡️ Следующее место")
# async def next_place(message: Message, session: AsyncSession):
#     await show_next_place(message, session)
#
#
# @feed_router.message(F.text == "❤️ Лайк")
# async def like_place(message: Message, session: AsyncSession):
#     user_id = message.from_user.id
#     feed_state = await get_or_create_feed_state(session, user_id)
#
#     if feed_state.last_place_id:
#         await update_place_history(session, user_id, feed_state.last_place_id, liked=True)
#         await message.answer("👍 Место понравилось! Учту твой выбор.")
#
#     await show_next_place(message, session)
#
#
# @feed_router.message(F.text == "👎 Дизлайк")
# async def dislike_place(message: Message, session: AsyncSession):
#     user_id = message.from_user.id
#     feed_state = await get_or_create_feed_state(session, user_id)
#
#     if feed_state.last_place_id:
#         await update_place_history(session, user_id, feed_state.last_place_id, disliked=True)
#         await message.answer("👎 Понятно, больше не покажу подобное.")
#
#     await show_next_place(message, session)
#
#
# @feed_router.message(F.text == "📌 Сохранить")
# async def save_place(message: Message, session: AsyncSession):
#     user_id = message.from_user.id
#     feed_state = await get_or_create_feed_state(session, user_id)
#
#     if feed_state.last_place_id:
#         await update_place_history(session, user_id, feed_state.last_place_id, saved=True)
#         await message.answer("📌 Место сохранено в избранное!")
#
#     await show_next_place(message, session)
#
#
# @feed_router.message(F.text == "🗺️ Обновить локацию")
# async def update_location(message: Message):
#     location_keyboard = ReplyKeyboardMarkup(
#         keyboard=[
#             [KeyboardButton(text="📍 Отправить местоположение", request_location=True)]
#         ],
#         resize_keyboard=True,
#         one_time_keyboard=True
#     )
#
#     await message.answer(
#         "📍 Обнови свое местоположение для точного поиска:",
#         reply_markup=location_keyboard
#     )