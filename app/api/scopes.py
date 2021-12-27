from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy import func, select
from sqlalchemy.orm.session import Session
from starlette.responses import Response

from app.deps.db import get_db
from app.deps.scopes import query_user_scopes
from app.deps.users import manager
from app.deps.request_params import parse_react_admin_params
from app.models.scope import Scope
from app.models.user import User
from app.schemas.scope import Scope as ScopeSchema
from app.schemas.scope import ScopeCreate, ScopeUpdate
from app.schemas.request_params import RequestParams
from app.core.logger import logger

router = APIRouter(prefix="/scopes")


@router.get("", response_model=List[ScopeSchema], status_code=200)
def get_scopes(
    response: Response,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["scopes_get"]),
    request_params: RequestParams = Depends(parse_react_admin_params(Scope)),
) -> Any:
    total = db.scalar(select(func.count(Scope.name)))
    scopes = (
        db.execute(
            select(Scope)
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
    ] = f"{request_params.skip}-{request_params.skip + len(scopes)}/{total}"

    logger.info(f"{user} getting all scopes with status code {response.status_code}")
    return scopes


@router.get("/user/{user_id}", response_model=List[ScopeSchema], status_code=200)
def get_user_scopes(
    response: Response,
    user_id: UUID,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["scopes_get"]),
    request_params: RequestParams = Depends(parse_react_admin_params(Scope)),
) -> Any:
    user_queried: Optional[User] = db.get(User, user_id)
    if not user_queried:
        raise HTTPException(404)

    user_scopes = query_user_scopes(user_queried, db)
    user_scopes_names = [user_scope.scope_name for user_scope in user_scopes]

    total = db.scalar(
        select(func.count(Scope.name)).where(Scope.name in user_scopes_names)
    )
    scopes = (
        db.execute(
            select(Scope)
            .where(Scope.name in user_scopes_names)
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
    ] = f"{request_params.skip}-{request_params.skip + len(scopes)}/{total}"

    logger.info(
        f"{user} getting scopes for {user_queried} with status code {response.status_code}"
    )
    return scopes


@router.post("", response_model=ScopeSchema, status_code=201)
def create_scope(
    scope_in: ScopeCreate,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["scopes_create"]),
) -> Any:
    scope = Scope(**scope_in.dict())
    db.add(scope)
    db.commit()

    logger.info(f"{user} creating scope {scope.name}")
    return scope


@router.put("/{scope_name}", response_model=ScopeSchema, status_code=200)
def update_scope(
    scope_name: str,
    scope_in: ScopeUpdate,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["scopes_update"]),
) -> Any:
    scope: Optional[Scope] = db.get(Scope, scope_name)
    if not scope:
        raise HTTPException(404)
    update_data = scope_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(scope, field, value)
    db.add(scope)
    db.commit()

    logger.info(f"{user} updating scope {scope.name}")
    return scope


@router.get("/{scope_name}", response_model=ScopeSchema)
def get_scope(
    scope_name: str,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["scopes_get"]),
) -> Any:
    scope: Optional[Scope] = db.get(Scope, scope_name)
    if not scope:
        raise HTTPException(404)

    logger.info(f"{user} getting scope {scope.name}")
    return scope
