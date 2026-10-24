from aiogram import Router
from . import categories, common, tasks, fallback

def get_routers() -> list[Router]:
    return [ common.router, tasks.router, categories.router, fallback.router]
