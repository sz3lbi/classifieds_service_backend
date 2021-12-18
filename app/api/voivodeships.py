from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm.session import Session
from starlette.responses import Response

from app.deps.db import get_db
from app.deps.request_params import parse_react_admin_params
from app.deps.users import current_user
from app.models.voivodeship import Voivodeship
from app.models.user import User
from app.schemas.voivodeship import Voivodeship as VoivodeshipSchema
from app.schemas.voivodeship import VoivodeshipCreate, VoivodeshipUpdate
from app.schemas.request_params import RequestParams
from app.core.logger import logger

router = APIRouter(prefix="/voivodeships")


@router.get("", response_model=List[VoivodeshipSchema])
def get_voivodeships(
    response: Response,
    db: Session = Depends(get_db),
    request_params: RequestParams = Depends(parse_react_admin_params(Voivodeship)),
    user: User = Depends(current_user),
) -> Any:
    total = db.scalar(select(func.count(Voivodeship.id)))
    voivodeships = (
        db.execute(
            select(Voivodeship)
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
    ] = f"{request_params.skip}-{request_params.skip + len(voivodeships)}/{total}"

    logger.info(
        f"User {user} getting all voivodeships with status code {response.status_code}"
    )
    return voivodeships


@router.post("", response_model=VoivodeshipSchema, status_code=201)
def create_voivodeship(
    voivodeship_in: VoivodeshipCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> Any:
    voivodeship = Voivodeship(**voivodeship_in.dict())
    db.add(voivodeship)
    db.commit()

    logger.info(
        f"User {user} creating voivodeship {voivodeship.name} (ID {voivodeship.id})"
    )
    return voivodeship


@router.put("/{voivodeship_id}", response_model=VoivodeshipSchema)
def update_voivodeship(
    voivodeship_id: int,
    voivodeship_in: VoivodeshipUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> Any:
    voivodeship: Optional[Voivodeship] = db.get(Voivodeship, voivodeship_id)
    if not voivodeship:
        raise HTTPException(404)
    update_data = voivodeship_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(voivodeship, field, value)
    db.add(voivodeship)
    db.commit()

    logger.info(f"User {user} updating voivodeship (ID {voivodeship.id})")
    return voivodeship


@router.get("/{voivodeship_id}", response_model=VoivodeshipSchema)
def get_voivodeship(
    voivodeship_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> Any:
    voivodeship: Optional[Voivodeship] = db.get(Voivodeship, voivodeship_id)
    if not voivodeship:
        raise HTTPException(404)

    logger.info(f"User {user} getting voivodeship (ID {voivodeship.id})")
    return voivodeship


@router.delete("/{voivodeship_id}")
def delete_voivodeship(
    voivodeship_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> Any:
    voivodeship: Optional[Voivodeship] = db.get(Voivodeship, voivodeship_id)
    if not voivodeship:
        raise HTTPException(404)
    db.delete(voivodeship)
    db.commit()

    logger.info(f"User {user} deleting voivodeship (ID {voivodeship.id})")
    return {"success": True}
