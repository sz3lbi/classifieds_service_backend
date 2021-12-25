from datetime import timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm.session import Session
from fastapi_login import LoginManager
from pydantic import EmailStr
from passlib.context import CryptContext

from app.models.user import User
from app.core.config import settings
from app.deps.db import ContextManager, get_db

manager = LoginManager(
    secret=settings.SECRET_KEY,
    token_url="/login",
    default_expiry=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


@manager.user_loader()
def query_user(id: UUID, db_session: Session = None):
    if not db_session:
        with ContextManager() as db_session:
            user = (
                db_session.execute(select(User).where(User.id == id)).scalars().first()
            )
            return user
    try:
        user = db_session.execute(select(User).where(User.id == id)).scalars().first()
    except:
        return None
    return user


def query_user_by_email(email: EmailStr, db_session: Session):
    user = db_session.execute(select(User).where(User.email == email)).scalars().first()
    return user
