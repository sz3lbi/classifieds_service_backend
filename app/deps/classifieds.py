from datetime import timedelta

from app.models.classified import Classified, ClassifiedStatus
from app.core.config import settings
from app.core.logger import logger
from app.deps.db import DBSessionManager

expire_time = timedelta(days=settings.classified_expire_time_days)


async def hide_expired_classifieds(ctx):
    job_id = ctx["job_id"]

    with DBSessionManager() as db:
        elapsed = (Classified.updated - Classified.created).label("elapsed")
        query_classifieds = db.query(Classified).filter(elapsed >= expire_time)
        classifieds = query_classifieds.all()
        for classified in classifieds:
            classified.status = ClassifiedStatus.hidden
            db.add(classified)
        db.commit()
        logger.info(f"Job ID {job_id} hiding expired classifieds")
