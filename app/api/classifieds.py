from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from starlette.responses import Response

from app.deps.db import get_db
from app.deps.users import manager
from app.deps.request_params import parse_react_admin_params
from app.models.classified import Classified
from app.models.category import Category
from app.models.user import User
from app.schemas.classified import Classified as ClassifiedSchema
from app.schemas.classified import ClassifiedCreate, ClassifiedUpdate
from app.schemas.request_params import RequestParams
from app.core.logger import logger

router = APIRouter(prefix="/classifieds")


@router.get("/category/{category_id}", response_model=List[ClassifiedSchema])
def get_category_classifieds(
    response: Response,
    category_id: int,
    db: Session = Depends(get_db),
    request_params: RequestParams = Depends(parse_react_admin_params(Classified)),
) -> Any:
    category: Optional[Category] = db.get(Category, category_id)
    if not category:
        raise HTTPException(404)

    total = (
        db.query(func.count(Classified.id))
        .filter(Classified.category == category)
        .scalar()
    )
    query_classifieds = (
        db.query(Classified)
        .filter(Classified.category == category)
        .order_by(request_params.order_by)
    )
    classifieds = (
        query_classifieds.offset(request_params.skip).limit(request_params.limit).all()
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(classifieds)}/{total}"

    logger.info(f"Getting all classifieds for category {category.name}")
    return classifieds


@router.post("", response_model=ClassifiedSchema, status_code=201)
def create_classified(
    classified_in: ClassifiedCreate,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["classifieds_create"]),
) -> Any:
    classified = Classified(**classified_in.dict())
    classified.user_id = user.id
    db.add(classified)
    db.commit()

    logger.info(f"{user} creating classified {classified.title} (ID {classified.id})")
    return classified


@router.put("/{classified_id}", response_model=ClassifiedSchema)
def update_classified(
    classified_id: int,
    classified_in: ClassifiedUpdate,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["classifieds_update"]),
) -> Any:
    classified: Optional[Classified] = db.get(Classified, classified_id)
    if not classified:
        raise HTTPException(404)
    if classified.user_id != user.id and not user.is_superuser:
        raise HTTPException(401)
    update_data = classified_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(classified, field, value)
    db.add(classified)
    db.commit()

    logger.info(f"{user} updating classified (ID {classified.id})")
    return classified


@router.get("/{classified_id}", response_model=ClassifiedSchema)
def get_classified(
    classified_id: int,
    db: Session = Depends(get_db),
) -> Any:
    classified: Optional[Classified] = db.get(Classified, classified_id)
    if not classified:
        raise HTTPException(404)

    logger.info(f"Getting classified (ID {classified.id})")
    return classified


@router.delete("/{classified_id}")
def delete_classified(
    classified_id: int,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["classifieds_delete"]),
) -> Any:
    classified: Optional[Classified] = db.get(Classified, classified_id)
    if not classified:
        raise HTTPException(404)
    if classified.user_id != user.id and not user.is_superuser:
        raise HTTPException(401)
    db.delete(classified)
    db.commit()

    logger.info(f"{user} deleting classified (ID {classified.id})")
    return {"success": True}
