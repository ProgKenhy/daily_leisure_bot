from aiogram import Router
from users.routers import users_router

main_router = Router()

main_router.include_router(users_router)

__all__ = ['main_router']