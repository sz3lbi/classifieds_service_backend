from app.db import SessionLocal


class DBSessionManager:
    def __init__(self):
        self.db = SessionLocal(future=True)

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()


async def get_db():
    with DBSessionManager() as db:
        yield db
