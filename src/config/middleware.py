from .database import async_session_factory
from typing import Callable, Any
from config.settings import settings
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
import logging

logger = logging.getLogger(__name__)

class DatabaseMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        async with async_session_factory() as session:
            data["session"] = session
            try:
                return await handler(event, data)
            finally:
                await session.close()


class AdminMiddleware(BaseMiddleware):
    def __init__(self):
        self.admin_ids = settings.ADMIN_IDS
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Any],
            event: TelegramObject,
            data: dict[str, Any]
    ) -> Any:
        if hasattr(event, 'from_user'):
            user_id = str(event.from_user.id)
            username = getattr(event.from_user, 'username', 'Unknown')

            logger.info(f"Admin middleware check for user {user_id} (@{username})")

            if user_id not in self.admin_ids:
                logger.warning(f"Unauthorized admin access attempt by user {user_id} (@{username})")
                if hasattr(event, 'answer'):
                    await event.answer("❌ Доступ запрещен")
                elif hasattr(event, 'message') and hasattr(event.message, 'answer'):
                    await event.message.answer("❌ Доступ запрещен")
                return None

            logger.info(f"Admin access granted to user {user_id} (@{username})")

        return await handler(event, data)