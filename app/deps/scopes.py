from typing import List
from sqlalchemy.orm.session import Session
from app.deps.db import DBSessionManager

from app.models.user import User
from app.models.user_scope import UserScope
from app.models.scope import Scope


def query_scopes(db_session: Session = None):
    if not db_session:
        with DBSessionManager() as db_session:
            query_scopes = db_session.query(Scope)
            scopes = query_scopes.all()
            return scopes
    try:
        query_scopes = db_session.query(Scope)
        scopes = query_scopes.all()
    except:
        return None
    return scopes


def query_scopes_dict(db_session: Session = None):
    scopes = query_scopes(db_session)
    scopes_dict = {}
    for scope in scopes:
        scopes_dict[scope.scope_name] = scope.description
    return scopes_dict


def query_scope_names_for_user(user: User, db_session: Session) -> List[str]:
    if user.is_superuser:
        scopes = query_scopes(db_session)
        names = [scope.scope_name for scope in scopes]
        return names

    query_user_scopes = db_session.query(UserScope).filter(UserScope.user_id == user.id)
    user_scopes = query_user_scopes.all()
    names = [user_scope.scope_name for user_scope in user_scopes]
    return names
