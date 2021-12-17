from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi_users import FastAPIUsers
from starlette.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.deps.users import fastapi_users, jwt_authentication


def create_app():
    description = f"{settings.PROJECT_NAME} API"
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_PATH}/openapi.json",
        docs_url="/docs/",
        description=description,
        redoc_url=None,
    )
    setup_routers(app, fastapi_users)
    init_db_hooks(app)
    setup_cors_middleware(app)
    return app


def setup_routers(app: FastAPI, fastapi_users: FastAPIUsers) -> None:
    app.include_router(api_router, prefix=settings.API_PATH)
    app.include_router(
        fastapi_users.get_auth_router(
            jwt_authentication,
            requires_verification=False,
        ),
        prefix=f"{settings.API_PATH}/auth/jwt",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_register_router(),
        prefix=f"{settings.API_PATH}/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_users_router(requires_verification=False),
        prefix=f"{settings.API_PATH}/users",
        tags=["users"],
    )
    # The following operation needs to be at the end of this function
    use_route_names_as_operation_ids(app)


def setup_cors_middleware(app):
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            expose_headers=["Content-Range", "Range"],
            allow_headers=["Authorization", "Range", "Content-Range"],
        )


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    route_names = set()
    for route in app.routes:
        if isinstance(route, APIRoute):
            name = route.name
            # Appending route methods to patch fastapi-users bug
            # where multiple routes with different methods have the same name
            if name.startswith("users"):
                methods_joined = "_".join(route.methods).lower()    
                name = f"{name}_{methods_joined}"
            if name in route_names:
                raise Exception("Route function names should be unique")                    
            route.operation_id = name
            route_names.add(name)


def init_db_hooks(app: FastAPI) -> None:
    from app.db import database

    @app.on_event("startup")
    async def startup():
        await database.connect()

    @app.on_event("shutdown")
    async def shutdown():
        await database.disconnect()
