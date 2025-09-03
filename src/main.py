import asyncio
import logging
from config.middleware import DatabaseMiddleware
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.routers import main_router

from config.settings import settings

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting bot")
    bot = Bot(token=settings.bot.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(main_router)
    dp.message.middleware(DatabaseMiddleware())

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())