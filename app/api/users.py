from os import stat
from typing import Any, List
from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.routing import APIRouter
from sqlalchemy import func, select
from sqlalchemy.orm.session import Session
from starlette.responses import Response
from fastapi_login.exceptions import InvalidCredentialsException

from app.deps.db import get_db
from app.deps.users import (
    manager,
    verify_password,
    get_password_hash,
    query_user_by_email,
)
from app.models.user import User
from app.schemas.user import User as UserSchema, UserDB
from app.schemas.user import UserCreate
from app.core.logger import logger

router = APIRouter()


@router.post("/login", name="users:login", status_code=200)
def login(db: Session = Depends(get_db), data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = query_user_by_email(email, db)
    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/register", name="users:register", response_model=UserSchema, status_code=201
)
def login(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = query_user_by_email(user_in.email, db)
    if existing_user is not None:
        raise HTTPException(
            status_code=400,
            detail=f"User already exists",
        )

    hashed_password = get_password_hash(user_in.password)

    user = User(email=user_in.email, hashed_password=hashed_password)
    db.add(user)
    db.commit()

    return user


@router.get("/users", response_model=List[UserSchema], status_code=200)
def get_users(
    response: Response,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user: User = Depends(manager),
) -> Any:

    if user is None:
        logger.info("Unauthorized user tried to get users list.")
        raise HTTPException(401)
    elif not user.is_superuser:
        logger.info(f"Not-superuser {user} tried to get users list.")
        raise HTTPException(401)

    total = db.scalar(select(func.count(User.id)))
    users = db.execute(select(User).offset(skip).limit(limit)).scalars().all()
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers["Content-Range"] = f"{skip}-{skip + len(users)}/{total}"

    logger.info(f"{user} getting all users with status code {response.status_code}")
    return users
