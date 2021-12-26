from sqlalchemy import select
from sqlalchemy.orm.session import Session
from app.deps.db import DBSessionManager

from app.models.user import User
from app.models.user_scope import UserScope
from app.models.scope import Scope


def query_scopes(db_session: Session = None):
    if not db_session:
        with DBSessionManager() as db_session:
            scopes = db_session.execute(select(Scope)).scalars().all()
            return scopes
    try:
        scopes = db_session.execute(select(Scope)).scalars().all()
    except:
        return None
    return scopes


def query_scopes_dict(db_session: Session = None):
    scopes = query_scopes(db_session)
    scopes_dict = {}
    for scope in scopes:
        scopes_dict[scope.name] = scope.description
    return scopes_dict


def query_user_scopes(user: User, db_session: Session):
    if user.is_superuser:
        return query_scopes(db_session)

    user_scopes = (
        db_session.execute(select(UserScope).where(UserScope.user_id == user.id))
        .scalars()
        .all()
    )
    return user_scopes
