from aiogram import Router
from users.routers import users_router
from feed.routers import feed_router

main_router = Router()

main_router.include_router(users_router)
main_router.include_router(feed_router)

__all__ = ['main_router']