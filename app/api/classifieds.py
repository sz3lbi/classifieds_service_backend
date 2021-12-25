from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
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

    total = db.scalar(select(func.count(Classified.id)))
    classifieds = (
        db.execute(
            select(Classified)
            .where(Classified.category == category)
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
    ] = f"{request_params.skip}-{request_params.skip + len(classifieds)}/{total}"

    logger.info(
        f"Getting all classifieds for category {category.name} with status code {response.status_code}"
    )
    return classifieds


@router.post("", response_model=ClassifiedSchema, status_code=201)
def create_classified(
    classified_in: ClassifiedCreate,
    db: Session = Depends(get_db),
    user: User = Depends(manager),
) -> Any:
    classified = Classified(**classified_in.dict())
    classified.user_id = user.id
    db.add(classified)
    db.commit()

    logger.info(
        f"User {user} creating classified {classified.name} (ID {classified.id})"
    )
    return classified


@router.put("/{classified_id}", response_model=ClassifiedSchema)
def update_classified(
    classified_id: int,
    classified_in: ClassifiedUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(manager),
) -> Any:
    classified: Optional[Classified] = db.get(Classified, classified_id)
    if not classified or (classified.user_id != user.id and not user.is_superuser):
        raise HTTPException(404)
    update_data = classified_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(classified, field, value)
    db.add(classified)
    db.commit()

    logger.info(f"User {user} updating classified (ID {classified.id})")
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
    user: User = Depends(manager),
) -> Any:
    classified: Optional[Classified] = db.get(Classified, classified_id)
    if not classified or (classified.user_id != user.id and not user.is_superuser):
        raise HTTPException(404)
    db.delete(classified)
    db.commit()

    logger.info(f"User {user} deleting classified (ID {classified.id})")
    return {"success": True}
