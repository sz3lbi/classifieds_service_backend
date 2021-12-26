from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy import func, select
from sqlalchemy.orm.session import Session
from starlette.responses import Response

from app.deps.db import get_db
from app.deps.users import manager
from app.deps.request_params import parse_react_admin_params
from app.models.user_scope import UserScope
from app.models.user import User
from app.schemas.user_scope import UserScope as UserScopeSchema
from app.schemas.user_scope import UserScopeCreate
from app.schemas.request_params import RequestParams
from app.core.logger import logger

router = APIRouter(prefix="/users_scopes")


@router.get("", response_model=List[UserScopeSchema])
def get_users_scopes(
    response: Response,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["users_scopes_get"]),
    request_params: RequestParams = Depends(parse_react_admin_params(UserScope)),
) -> Any:
    total = db.scalar(select(func.count(UserScope.scope_name)))
    users_scopes = (
        db.execute(
            select(UserScope)
            .offset(request_params.skip)
            .limit(request_params.limit)
            .order_by(request_params.order_by)
        )
        .scalars()
        .all()
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(users_scopes)}/{total}"

    logger.info(
        f"{user} getting all users_scopes with status code {response.status_code}"
    )
    return users_scopes


@router.get("/user/{user_id}", response_model=List[UserScopeSchema])
def get_users_scopes_for_user(
    response: Response,
    user_id: UUID,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["users_scopes_get"]),
    request_params: RequestParams = Depends(parse_react_admin_params(UserScope)),
) -> Any:
    user_queried: Optional[User] = db.get(User, user_id)
    if not user_queried:
        raise HTTPException(404)

    total = db.scalar(
        select(func.count(UserScope.id)).where(UserScope.user_id == user_queried.id)
    )
    users_scopes = (
        db.execute(
            select(UserScope)
            .where(UserScope.user_id == user_queried.id)
            .offset(request_params.skip)
            .limit(request_params.limit)
            .order_by(request_params.order_by)
        )
        .scalars()
        .all()
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(users_scopes)}/{total}"

    logger.info(
        f"{user} getting users_scopes for user ID {user_queried.id} with status code {response.status_code}"
    )
    return users_scopes


@router.post("", response_model=UserScopeSchema, status_code=201)
def create_user_scope(
    user_scope_in: UserScopeCreate,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["users_scopes_create"]),
) -> Any:
    user_scope = UserScope(**user_scope_in.dict())
    user_scope.user_id = user.id
    db.add(user_scope)
    db.commit()

    logger.info(
        f"{user} creating user_scope for user ID {user_scope.user_id} and scope {user_scope.scope_name}"
    )
    return user_scope


@router.get("/{user_scope_id}", response_model=UserScopeSchema)
def get_user_scope(
    user_scope_id: int,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["users_scopes_get"]),
) -> Any:
    user_scope: Optional[UserScope] = db.get(UserScope, user_scope_id)
    if not user_scope:
        raise HTTPException(404)

    logger.info(
        f"{user} getting user_scope (user ID {user_scope.user_id}, scope {user_scope.scope_name})"
    )
    return user_scope


@router.delete("/{user_scope_id}")
def delete_user_scope(
    user_scope_id: int,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["users_scopes_delete"]),
) -> Any:
    user_scope: Optional[UserScope] = db.get(UserScope, user_scope_id)
    if not user_scope or (user_scope.user_id != user.id and not user.is_superuser):
        raise HTTPException(404)
    db.delete(user_scope)
    db.commit()

    logger.info(
        f"{user} deleting user_scope (user ID {user_scope.user_id}, scope {user_scope.scope_name})"
    )
    return {"success": True}
