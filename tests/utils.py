import secrets
import string
from typing import Any

from app.deps.users import manager
from app.models.user import User


def generate_random_string(length: int) -> str:
    return "".join(secrets.choice(string.ascii_lowercase) for i in range(length))


def get_jwt_header(user: User) -> Any:
    token = manager.create_access_token(data={"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}
