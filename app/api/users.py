from typing import Any, List, Optional
from fastapi import HTTPException, Security
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.routing import APIRouter
from sqlalchemy import func, select
from sqlalchemy.orm.session import Session
from starlette.responses import Response
from fastapi_login.exceptions import InvalidCredentialsException

from app.deps.db import get_db
from app.deps.scopes import query_user_scopes
from app.deps.users import (
    manager,
    verify_password,
    validate_password,
    get_password_hash,
    query_user_by_email,
)
from app.models.user import User
from app.models.user_scope import UserScope
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate
from app.models.scope import Scope
from app.core.logger import logger
from app.core.config import settings

router = APIRouter()


@router.post("/login", status_code=200)
def login(db: Session = Depends(get_db), data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = query_user_by_email(email, db)
    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsException
    user_scopes = query_user_scopes(user, db)
    user_scopes_names = [user_scope.name for user_scope in user_scopes]

    access_token = manager.create_access_token(
        data={"sub": str(user.id)}, scopes=user_scopes_names
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserSchema, status_code=201)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = query_user_by_email(user_in.email, db)
    if existing_user is not None:
        raise HTTPException(
            status_code=400,
            detail=f"User already exists",
        )

    validate_password(**user_in.dict())
    hashed_password = get_password_hash(user_in.password)

    user = User(email=user_in.email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    logger.info(f"{user} has registered.")

    for scope_name in settings.USER_DEFAULT_SCOPES:
        scope: Optional[Scope] = db.get(Scope, scope_name)
        if not scope:
            logger.error(
                f"User default scope {scope_name} does not exist in the database."
            )
            continue
        user_scope = UserScope(user_id=user.id, scope_name=scope.name)
        db.add(user_scope)

    db.commit()
    logger.info(f"User default scopes for {user} has been added.")

    return user


@router.get("/users", response_model=List[UserSchema], status_code=200)
def get_users(
    response: Response,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user: User = Security(manager, scopes=["users_get"]),
) -> Any:
    total = db.scalar(select(func.count(User.id)))
    users = db.execute(select(User).offset(skip).limit(limit)).scalars().all()
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers["Content-Range"] = f"{skip}-{skip + len(users)}/{total}"

    logger.info(f"{user} getting all users with status code {response.status_code}")
    return users
