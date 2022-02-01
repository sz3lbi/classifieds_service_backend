import asyncio

from aioredis.util import parse_url
from arq.worker import create_worker
from arq.connections import RedisSettings
from arq import cron

from app.core.config import settings
from app.deps.classifieds import hide_expired_classifieds


def redis_settings_from_uri(uri: str) -> RedisSettings:

    address, options = parse_url(uri)
    return RedisSettings(
        host=address[0], port=address[1], password=options.get("password")
    )


class WorkerSettings:
    functions = [hide_expired_classifieds]
    cron_jobs = [cron(hide_expired_classifieds, hour=3, minute=30, unique=True)]
    redis_settings = redis_settings_from_uri(uri=settings.REDIS_URL)


class Worker:
    def __init__(self):
        self.worker = None
        self.task = None

    async def start(self, **kwargs):
        self.worker = create_worker(WorkerSettings, **kwargs)
        self.task = asyncio.create_task(self.worker.async_run())

    async def close(self):
        await self.worker.close()


arq_worker = Worker()
