from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from starlette.responses import Response

from app.deps.db import get_db
from app.deps.users import manager
from app.deps.request_params import parse_react_admin_params
from app.models.city import City
from app.models.user import User
from app.schemas.city import City as CitySchema, CityDelete
from app.schemas.city import CityCreate, CityUpdate
from app.schemas.request_params import RequestParams
from app.core.logger import logger

router = APIRouter(prefix="/cities")


@router.get("", response_model=List[CitySchema])
def get_cities(
    response: Response,
    db: Session = Depends(get_db),
    request_params: RequestParams = Depends(parse_react_admin_params(City)),
) -> Any:
    total = db.query(func.count(City.id)).scalar()
    query_cities = db.query(City).order_by(request_params.order_by)
    cities = query_cities.offset(request_params.skip).limit(request_params.limit).all()
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(cities)}/{total}"

    logger.info(f"Getting all cities")
    return cities


@router.post("", response_model=CitySchema, status_code=201)
def create_city(
    city_in: CityCreate,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["cities_create"]),
) -> Any:
    city = City(**city_in.dict())
    db.add(city)
    db.commit()

    logger.info(f"{user} creating city {city.name} (ID {city.id})")
    return city


@router.put("/{city_id}", response_model=CitySchema)
def update_city(
    city_id: int,
    city_in: CityUpdate,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["cities_update"]),
) -> Any:
    city: Optional[City] = db.get(City, city_id)
    if not city:
        raise HTTPException(404)
    update_data = city_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(city, field, value)
    db.add(city)
    db.commit()

    logger.info(f"{user} updating city (ID {city.id})")
    return city


@router.get("/{city_id}", response_model=CitySchema)
def get_city(
    city_id: int,
    db: Session = Depends(get_db),
) -> Any:
    city: Optional[City] = db.get(City, city_id)
    if not city:
        raise HTTPException(404)

    logger.info(f"Getting city {city.name} (ID {city.id})")
    return city


@router.delete("/{city_id}", response_model=CityDelete)
def delete_city(
    city_id: int,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["cities_delete"]),
) -> Any:
    city: Optional[City] = db.get(City, city_id)
    if not city:
        raise HTTPException(404)
    db.delete(city)
    db.commit()

    logger.info(f"{user} deleting city {city.name} (ID {city.id})")
    return city
