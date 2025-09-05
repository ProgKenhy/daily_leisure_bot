# from aiogram import Router
# from aiogram.filters import Command, CommandStart
# from aiogram.types import Message
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from .models import User
#
# users_router = Router()
# @users_router.message(CommandStart())
# async def cmd_start(message: Message, session: AsyncSession):
#     await message.answer(text="Hello!")


from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import User

users_router = Router()

@users_router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession):
    # Проверяем, есть ли пользователь в БД
    stmt = select(User).where(User.tg_id == message.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        # Создаем нового пользователя
        new_user = User(
            tg_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        session.add(new_user)
        await session.commit()
        

#         # Просим локацию
#         location_keyboard = ReplyKeyboardMarkup(
#             keyboard=[[KeyboardButton(text="Поделиться местоположением", request_location=True)]],
#             resize_keyboard=True,
#             one_time_keyboard=True
#         )
#         await message.answer(
#             "Привет! Я помогу тебе найти интересные места рядом. Для начала поделись своим местоположением.",
#             reply_markup=location_keyboard
#         )
#     else:
#         # Пользователь уже есть, предлагаем посмотреть ленту
#         await message.answer("С возвращением! Напиши /feed чтобы посмотреть новые места.")