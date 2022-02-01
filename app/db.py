import databases
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import registry, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, future=True, pool_size=10)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

mapper_registry = registry()
Base: DeclarativeMeta = declarative_base()

database = databases.Database(settings.database_url)
