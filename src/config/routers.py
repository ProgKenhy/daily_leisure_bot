from aiogram import Router
from users.routers import users_router
# from feed.routers import feed_router
from feed.admin import admin_router as feed_admin_router

main_router = Router()

main_router.include_router(users_router)
# main_router.include_router(feed_router)

main_router.include_router(feed_admin_router)

__all__ = ['main_router']