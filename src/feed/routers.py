from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

feed_router = Router()

@feed_router.message(Command(commands='feed'))
async def cmd_feed(message: Message, session: AsyncSession):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Настолки"), KeyboardButton(text="Мероприятия"),]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        "Выбери сферу, которая тебя сегодня интересует.",
        reply_markup=keyboard
    )



