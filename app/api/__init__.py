from fastapi import APIRouter

from app.api import voivodeships, categories, users, utils

api_router = APIRouter()

api_router.include_router(utils.router, tags=["utils"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(categories.router, tags=["categories"])
api_router.include_router(voivodeships.router, tags=["voivodeships"])