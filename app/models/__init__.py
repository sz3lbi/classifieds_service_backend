# Import all models here so alembic can discover them
from app.db import Base

from app.models.category import Category
from app.models.city import City
from app.models.classified import Classified
from app.models.image import Image
from app.models.user import User
from app.models.voivodeship import Voivodeship
from app.models.scope import Scope
from app.models.user_scope import UserScope
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.conversation_user import ConversationUser
