from typing import Any, List, Optional

from fastapi import (
    Header,
    APIRouter,
    Depends,
    HTTPException,
    File,
    UploadFile,
    Security,
    Form,
)
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from starlette.responses import Response
from pathlib import Path

from app.deps.db import get_db
from app.deps.users import manager
from app.deps.request_params import parse_react_admin_params
from app.models.classified import Classified
from app.models.image import Image
from app.models.user import User
from app.schemas.image import Image as ImageSchema
from app.schemas.request_params import RequestParams
from app.core.logger import logger
from app.core.config import settings

import os
import shutil
import uuid


async def valid_content_length(
    content_length: int = Header(..., lt=settings.IMAGES_MAX_SIZE)
):
    return content_length


def save_upload_file(upload_file: UploadFile, destination: Path) -> None:
    try:
        upload_file.file.seek(0)
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()


router = APIRouter(prefix="/images")


@router.get("/classified/{classified_id}", response_model=List[ImageSchema])
def get_classified_images(
    response: Response,
    classified_id: int,
    db: Session = Depends(get_db),
    request_params: RequestParams = Depends(parse_react_admin_params(Image)),
) -> Any:
    classified: Optional[Image] = db.get(Classified, classified_id)
    if not classified:
        raise HTTPException(404)

    total = (
        db.query(func.count(Image.id))
        .filter(Image.classified_id == classified.id)
        .scalar()
    )
    query_images = (
        db.query(Image)
        .filter(Image.classified_id == classified.id)
        .order_by(request_params.order_by)
    )
    images = query_images.offset(request_params.skip).limit(request_params.limit).all()
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(images)}/{total}"

    logger.info(f"Getting images for classified {classified_id}")
    return images


@router.post(
    "",
    dependencies=[Depends(valid_content_length)],
    response_model=ImageSchema,
    status_code=201,
)
def create_image(
    classified_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["images_create"]),
) -> Any:
    classified: Optional[Classified] = db.get(Classified, classified_id)
    if not classified:
        raise HTTPException(404)
    if classified.user_id != user.id:
        logger.error(
            f"{user} tried to create image in other's user classified (ID {classified.id})"
        )
        raise HTTPException(401)

    if file.content_type not in settings.IMAGES_CONTENT_TYPES:
        logger.error(f"{user} tried to create image of type {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail=f"File type of {file.content_type} is not supported",
        )

    filename = uuid.uuid4()
    extension = Path(file.filename).suffix
    destination = f"{settings.IMAGES_UPLOAD_PATH}{filename}{extension}"
    save_upload_file(file, Path(destination))

    image = Image(filename=filename, extension=extension)
    image.classified_id = classified.id
    db.add(image)
    db.commit()

    logger.info(
        f"{user} creating image (ID {image.id}) at {destination} for classified (ID {classified.id})"
    )
    return image


@router.get("/{image_id}", response_class=FileResponse)
def get_image_file(
    image_id: int,
    db: Session = Depends(get_db),
) -> Any:
    image: Optional[Image] = db.get(Image, image_id)
    if not image:
        raise HTTPException(404)

    file_path = f"{settings.IMAGES_UPLOAD_PATH}{image.filename}{image.extension}"

    logger.info(f"Getting image {file_path} (ID {image.id})")
    return file_path


@router.delete("/{image_id}")
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    user: User = Security(manager, scopes=["images_delete"]),
) -> Any:
    image: Optional[Image] = db.get(Image, image_id)
    if not image:
        raise HTTPException(404)
    if image.user_id != user.id and not user.is_superuser:
        raise HTTPException(401)

    try:
        file_path = f"{settings.IMAGES_UPLOAD_PATH}{image.filename}{image.extension}"
        os.remove(file_path)
    except FileNotFoundError:
        logger.error(f"File not found when deleting image (ID {image.id})")

    db.delete(image)
    db.commit()

    logger.info(f"{user} deleting image (ID {image.id})")
    return {"success": True}
