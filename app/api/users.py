from typing import Any, List, Optional
from uuid import UUID
from fastapi import HTTPException, Security
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.routing import APIRouter
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from starlette.responses import Response
from fastapi_login.exceptions import InvalidCredentialsException

from app.deps.db import get_db
from app.deps.request_params import parse_react_admin_params
from app.deps.scopes import query_default_scopes_names, query_scope_names_for_user
from app.deps.users import (
    manager,
    verify_password,
    validate_password,
    get_password_hash,
    query_user_by_username,
    query_user_by_email,
)
from app.models.user import User
from app.models.user_scope import UserScope
from app.schemas import request_params
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate
from app.core.logger import logger

router = APIRouter()


@router.post("/login", status_code=200)
def login(db: Session = Depends(get_db), data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    password = data.password

    user = query_user_by_username(username, db)
    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsException
    scope_names = query_scope_names_for_user(user, db)

    access_token = manager.create_access_token(
        data={"sub": str(user.id)}, scopes=scope_names
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserSchema, status_code=201)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = query_user_by_username(user_in.username, db)
    if existing_user is not None:
        raise HTTPException(
            status_code=400,
            detail=f"User with the username provided already exists",
        )
    existing_user = query_user_by_email(user_in.email, db)
    if existing_user is not None:
        raise HTTPException(
            status_code=400,
            detail=f"User with the e-mail provided already exists",
        )

    validate_password(**user_in.dict())
    hashed_password = get_password_hash(user_in.password)

    user = User(
        username=user_in.username, email=user_in.email, hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    logger.info(f"{user} has registered.")

    default_scopes = query_default_scopes_names(db)
    for scope_name in default_scopes:
        user_scope = UserScope(user_id=user.id, scope_name=scope_name)
        db.add(user_scope)

    db.commit()
    logger.info(f"User default scopes for {user} has been added.")

    return user


@router.get("/users", response_model=List[UserSchema], status_code=200)
def get_users(
    response: Response,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["users"]),
    request_params: request_params = Depends(parse_react_admin_params(User)),
) -> Any:
    total = db.query(func.count(User.id)).scalar()
    query_users = db.query(User).order_by(request_params.order_by)
    users = query_users.offset(request_params.skip).limit(request_params.limit).all()
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(users)}/{total}"

    logger.info(f"{user} getting all users")
    return users


@router.get("/user/{user_id}", response_model=UserSchema, status_code=200)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["users"]),
) -> Any:
    user_queried: Optional[User] = db.get(User, user_id)
    if not user_queried:
        raise HTTPException(404)

    logger.info(f"{user} getting {user_queried}")
    return user_queried


@router.get("/users/me", response_model=UserSchema, status_code=200)
def get_user_me(
    user: User = Security(manager, scopes=["users"]),
) -> Any:
    return user
