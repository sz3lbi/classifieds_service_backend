from fastapi import APIRouter

from app.api import (
    messages,
    conversations_users,
    conversations,
    scopes,
    users_scopes,
    classifieds,
    images,
    cities,
    voivodeships,
    categories,
    users,
    utils,
)

api_router = APIRouter()

api_router.include_router(utils.router, tags=["utils"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(categories.router, tags=["categories"])
api_router.include_router(voivodeships.router, tags=["voivodeships"])
api_router.include_router(cities.router, tags=["cities"])
api_router.include_router(images.router, tags=["images"])
api_router.include_router(classifieds.router, tags=["classifieds"])
api_router.include_router(users_scopes.router, tags=["users_scopes"])
api_router.include_router(scopes.router, tags=["scopes"])
api_router.include_router(conversations.router, tags=["conversations"])
api_router.include_router(conversations_users.router, tags=["conversations_users"])
api_router.include_router(messages.router, tags=["messages"])
