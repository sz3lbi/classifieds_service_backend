import json
from typing import Optional

from fastapi import HTTPException, Query
from loguru import logger
from sqlalchemy import asc, desc
from sqlalchemy.ext.declarative import DeclarativeMeta

from app.schemas.request_params import RequestParams


def parse_react_admin_params(model: DeclarativeMeta) -> RequestParams:
    """Parses sort and range parameters coming from a react-admin request"""

    def inner(
        sort_: Optional[str] = Query(
            None,
            alias="sort",
            description='Format: `["field_name", "direction"]`',
            example='["id", "ASC"]',
        ),
        range_: Optional[str] = Query(
            None,
            alias="range",
            description="Format: `[start, end]`",
            example="[0, 10]",
        ),
    ):
        skip, limit = 0, 10
        if range_:
            start, end = json.loads(range_)
            skip, limit = start, (end - start + 1)

        if sort_:
            sort_column, sort_order = json.loads(sort_)
            if sort_order.lower() == "asc":
                direction = asc
            elif sort_order.lower() == "desc":
                direction = desc
            else:
                logger.error(f"Invalid sort direction ({sort_order})")
                raise HTTPException(400, f"Invalid sort direction ({sort_order})")
            try:
                order_by = direction(model.__table__.c[sort_column])
            except KeyError:
                logger.error(f"Invalid sort column ({sort_column}) for {model}")
                raise HTTPException(400, f"Invalid sort column ({sort_column})")
        else:
            try:
                order_by = desc(model.id)
            except AttributeError:
                logger.error(f"Default sort column (id) is invalid for {model}")
                raise HTTPException(400, f"Default sort column (id) is invalid")

        return RequestParams(skip=skip, limit=limit, order_by=order_by)

    return inner
