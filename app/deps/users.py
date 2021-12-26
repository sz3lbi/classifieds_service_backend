from datetime import timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm.session import Session
from fastapi import HTTPException
from fastapi_login import LoginManager
from pydantic import EmailStr
from passlib.context import CryptContext

from app.models.user import User
from app.core.config import settings
from app.deps.db import DBSessionManager
from app.deps.scopes import query_scopes_dict

manager = LoginManager(
    secret=settings.SECRET_KEY,
    token_url="/login",
    default_expiry=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    scopes=query_scopes_dict(),
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


@manager.user_loader()
def query_user(user_id: UUID, db_session: Session = None):
    if not db_session:
        with DBSessionManager() as db_session:
            user = (
                db_session.execute(select(User).where(User.id == user_id))
                .scalars()
                .first()
            )
            return user
    try:
        user = (
            db_session.execute(select(User).where(User.id == user_id)).scalars().first()
        )
    except:
        return None
    return user


def query_user_by_email(email: EmailStr, db_session: Session):
    user = db_session.execute(select(User).where(User.email == email)).scalars().first()
    return user


def validate_password(
    email: EmailStr,
    password: str,
) -> None:
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Password should be at least {settings.PASSWORD_MIN_LENGTH} characters long",
        )
    if email in password:
        raise HTTPException(
            status_code=400,
            detail="Password should not contain e-mail",
        )
    if not any(character.isupper() for character in password):
        raise HTTPException(
            status_code=400,
            detail="Password should contain an uppercase character",
        )
