import asyncio

from arq.worker import create_worker
from arq.connections import RedisSettings
from arq import cron

from app.deps.classifieds import hide_expired_classifieds


class WorkerSettings:
    functions = [hide_expired_classifieds]
    cron_jobs = [cron(hide_expired_classifieds, hour=3, minute=30, unique=True)]
    redis_settings = RedisSettings()


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
