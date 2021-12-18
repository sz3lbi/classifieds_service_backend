from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm.session import Session
from starlette.responses import Response

from app.deps.db import get_db
from app.deps.request_params import parse_react_admin_params
from app.deps.users import current_user
from app.models.city import City
from app.models.user import User
from app.schemas.city import City as CitySchema
from app.schemas.city import CityCreate, CityUpdate
from app.schemas.request_params import RequestParams
from app.core.logger import logger

router = APIRouter(prefix="/cities")


@router.get("", response_model=List[CitySchema])
def get_cities(
    response: Response,
    db: Session = Depends(get_db),
    request_params: RequestParams = Depends(parse_react_admin_params(City)),
    user: User = Depends(current_user),
) -> Any:
    total = db.scalar(select(func.count(City.id)))
    cities = (
        db.execute(
            select(City)
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
    ] = f"{request_params.skip}-{request_params.skip + len(cities)}/{total}"

    logger.info(
        f"User {user} getting all cities with status code {response.status_code}"
    )
    return cities


@router.post("", response_model=CitySchema, status_code=201)
def create_city(
    city_in: CityCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> Any:
    city = City(**city_in.dict())
    db.add(city)
    db.commit()

    logger.info(f"User {user} creating city {city.name} (ID {city.id})")
    return city


@router.put("/{city_id}", response_model=CitySchema)
def update_city(
    city_id: int,
    city_in: CityUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> Any:
    city: Optional[City] = db.get(City, city_id)
    if not city:
        raise HTTPException(404)
    update_data = city_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(city, field, value)
    db.add(city)
    db.commit()

    logger.info(f"User {user} updating city (ID {city.id})")
    return city


@router.get("/{city_id}", response_model=CitySchema)
def get_city(
    city_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> Any:
    city: Optional[City] = db.get(City, city_id)
    if not city:
        raise HTTPException(404)

    logger.info(f"User {user} getting city (ID {city.id})")
    return city


@router.delete("/{city_id}")
def delete_city(
    city_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> Any:
    city: Optional[City] = db.get(City, city_id)
    if not city:
        raise HTTPException(404)
    db.delete(city)
    db.commit()

    logger.info(f"User {user} deleting city (ID {city.id})")
    return {"success": True}
