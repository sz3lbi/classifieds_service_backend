import uuid
from typing import Callable, Generator

import pytest

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session, sessionmaker
from starlette.testclient import TestClient

from app.core.config import settings
from app.db import Base
from app.deps.db import get_db
from app.factory import create_app
from app.models.category import Category
from app.models.user import User
from app.deps.users import get_password_hash
from tests.utils import generate_random_string

engine = create_engine(
    settings.database_url,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="session")
def default_password():
    return generate_random_string(32)


@pytest.fixture(scope="session")
def app():
    return create_app()


@pytest.fixture(scope="session")
def client(app) -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def db() -> Generator:
    session = TestingSessionLocal()

    yield session

    session.rollback()
    session.commit()


@pytest.fixture(scope="session", autouse=True)
def override_get_db(app):
    db = None
    try:
        db = TestingSessionLocal()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        yield db
    finally:
        if db:
            db.close()
    app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def auto_rollback(db: Session):
    db.rollback()


@pytest.fixture(scope="session")
def create_user(db: Session, default_password: str):
    def inner():
        user = User(
            id=uuid.uuid4(),
            email=f"{generate_random_string(20)}@{generate_random_string(10)}.com",
            hashed_password=get_password_hash(default_password),
        )
        db.add(user)
        db.commit()
        return user

    return inner


@pytest.fixture(scope="session")
def create_superuser(db: Session, default_password: str):
    def inner():
        user = User(
            id=uuid.uuid4(),
            email=f"{generate_random_string(20)}@{generate_random_string(10)}.com",
            hashed_password=get_password_hash(default_password),
        )
        user.is_superuser = True
        db.add(user)
        db.commit()
        return user

    return inner


@pytest.fixture(scope="session")
def create_category(db: Session, create_user: Callable):
    def inner(user=None):
        if not user:
            user = create_user()
        category = Category(
            name="name",
            description="description",
        )
        db.add(category)
        db.commit()
        return category

    return inner
