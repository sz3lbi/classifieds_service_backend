from fastapi import APIRouter

from app.api import images, cities, voivodeships, categories, users, utils

api_router = APIRouter()

api_router.include_router(utils.router, tags=["utils"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(categories.router, tags=["categories"])
api_router.include_router(voivodeships.router, tags=["voivodeships"])
api_router.include_router(cities.router, tags=["cities"])
api_router.include_router(images.router, tags=["images"])
