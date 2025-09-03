from aiogram import BaseMiddleware
from .database import async_session_factory

class DatabaseMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        async with async_session_factory() as session:
            data["session"] = session
            try:
                return await handler(event, data)
            finally:
                await session.close()