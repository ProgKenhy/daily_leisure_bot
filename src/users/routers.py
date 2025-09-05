from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import User

users_router = Router()


@users_router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession):
    stmt = select(User).where(User.tg_id == message.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        new_user = User(
            tg_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        session.add(new_user)
        await session.commit()

    # keyboard = ReplyKeyboardMarkup(
    #     keyboard=[
    #         [KeyboardButton(text="📍 Отправить местоположение", request_location=True)]
    #     ],
    #     resize_keyboard=True,
    #     one_time_keyboard=True
    # )

    await message.answer(
        "👋 Привет! Я помогу найти интересные места рядом.\n"
        "Можешь использовать /feed для поиска мест рядом!\n",
        # "📍 Поделись своим местоположением, чтобы я мог предложить варианты рядом с тобой.",
        # reply_markup=keyboard
    )


@users_router.message(F.location)
async def handle_location(message: Message, session: AsyncSession):
    location = message.location
    latitude = location.latitude
    longitude = location.longitude


    stmt = select(User).filter_by(User.tg_id == message.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        user.loc_lat = latitude
        user.loc_lon = longitude
        await session.commit()

        await message.answer(
            f"📍 Отлично! Твоя локация сохранена.\n"
            f"Широта: {latitude}\n"
            f"Долгота: {longitude}\n\n"
            f"Теперь можешь использовать /feed для поиска мест рядом!",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer("❌ Не удалось сохранить локацию. Попробуй /start сначала.")
