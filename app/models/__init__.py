# Import all models here so alembic can discover them
from fastapi_users.db import SQLAlchemyBaseUserTable

from app.db import Base

from app.models.category import Category
from app.models.city import City
from app.models.classified import Classified
from app.models.image import Image
from app.models.user import User
from app.models.voivodeship import Voivodeship