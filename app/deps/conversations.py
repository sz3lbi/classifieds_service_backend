from sqlalchemy import select
from sqlalchemy.orm.session import Session

from app.models.user import User
from app.models.conversation_user import ConversationUser


def query_user_conversations(user: User, db_session: Session):
    user_conversations = (
        db_session.execute(
            select(ConversationUser).where(ConversationUser.user_id == user.id)
        )
        .scalars()
        .all()
    )
    return user_conversations
