from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from starlette.responses import Response

from app.deps.db import get_db
from app.deps.users import manager
from app.deps.request_params import parse_react_admin_params
from app.models.voivodeship import Voivodeship
from app.models.user import User
from app.schemas.voivodeship import Voivodeship as VoivodeshipSchema, VoivodeshipDelete
from app.schemas.voivodeship import VoivodeshipCreate, VoivodeshipUpdate
from app.schemas.request_params import RequestParams
from app.core.logger import logger

router = APIRouter(prefix="/voivodeships")


@router.get("", response_model=List[VoivodeshipSchema])
def get_voivodeships(
    response: Response,
    db: Session = Depends(get_db),
    request_params: RequestParams = Depends(parse_react_admin_params(Voivodeship)),
) -> Any:
    total = db.query(func.count(Voivodeship.id)).scalar()
    query_voivodeships = db.query(Voivodeship).order_by(request_params.order_by)
    voivodeships = (
        query_voivodeships.offset(request_params.skip).limit(request_params.limit).all()
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(voivodeships)}/{total}"

    logger.info(f"Getting all voivodeships")
    return voivodeships


@router.post("", response_model=VoivodeshipSchema, status_code=201)
def create_voivodeship(
    voivodeship_in: VoivodeshipCreate,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["voivodeships_create"]),
) -> Any:
    voivodeship = Voivodeship(**voivodeship_in.dict())
    db.add(voivodeship)
    db.commit()

    logger.info(f"{user} creating voivodeship {voivodeship.name} (ID {voivodeship.id})")
    return voivodeship


@router.put("/{voivodeship_id}", response_model=VoivodeshipSchema)
def update_voivodeship(
    voivodeship_id: int,
    voivodeship_in: VoivodeshipUpdate,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["voivodeships_update"]),
) -> Any:
    voivodeship: Optional[Voivodeship] = db.get(Voivodeship, voivodeship_id)
    if not voivodeship:
        raise HTTPException(404)
    update_data = voivodeship_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(voivodeship, field, value)
    db.add(voivodeship)
    db.commit()

    logger.info(f"{user} updating voivodeship ID {voivodeship.id}")
    return voivodeship


@router.get("/{voivodeship_id}", response_model=VoivodeshipSchema)
def get_voivodeship(
    voivodeship_id: int,
    db: Session = Depends(get_db),
) -> Any:
    voivodeship: Optional[Voivodeship] = db.get(Voivodeship, voivodeship_id)
    if not voivodeship:
        raise HTTPException(404)

    logger.info(f"Getting voivodeship ID {voivodeship.id}")
    return voivodeship


@router.delete("/{voivodeship_id}", response_model=VoivodeshipDelete)
def delete_voivodeship(
    voivodeship_id: int,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["voivodeships_delete"]),
) -> Any:
    voivodeship: Optional[Voivodeship] = db.get(Voivodeship, voivodeship_id)
    if not voivodeship:
        raise HTTPException(404)
    db.delete(voivodeship)
    db.commit()

    logger.info(f"{user} deleting voivodeship ID {voivodeship.id}")
    return voivodeship
