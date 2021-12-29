from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from starlette.responses import Response

from app.deps.db import get_db
from app.deps.users import manager
from app.deps.request_params import parse_react_admin_params
from app.models.category import Category
from app.models.user import User
from app.schemas.category import Category as CategorySchema
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.request_params import RequestParams
from app.core.logger import logger

router = APIRouter(prefix="/categories")


@router.get("", response_model=List[CategorySchema])
def get_categories(
    response: Response,
    db: Session = Depends(get_db),
    request_params: RequestParams = Depends(parse_react_admin_params(Category)),
) -> Any:
    total = db.query(func.count(Category.id)).scalar()
    query_categories = db.query(Category).order_by(request_params.order_by)
    categories = (
        query_categories.offset(request_params.skip).limit(request_params.limit).all()
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(categories)}/{total}"

    logger.info(f"Getting all categories")
    return categories


@router.post("", response_model=CategorySchema, status_code=201)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["categories_create"]),
) -> Any:
    category = Category(**category_in.dict())
    db.add(category)
    db.commit()

    logger.info(f"{user} creating category {category.name} ID {category.id}")
    return category


@router.put("/{category_id}", response_model=CategorySchema)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["categories_update"]),
) -> Any:
    category: Optional[Category] = db.get(Category, category_id)
    if not category:
        raise HTTPException(404)
    update_data = category_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    db.add(category)
    db.commit()

    logger.info(f"{user} updating category ID {category.id}")
    return category


@router.get("/{category_id}", response_model=CategorySchema)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
) -> Any:
    category: Optional[Category] = db.get(Category, category_id)
    if not category:
        raise HTTPException(404)

    logger.info(f"Getting category ID {category.id}")
    return category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["categories_delete"]),
) -> Any:
    category: Optional[Category] = db.get(Category, category_id)
    if not category:
        raise HTTPException(404)
    db.delete(category)
    db.commit()

    logger.info(f"{user} deleting category ID {category.id}")
    return {"success": True}
