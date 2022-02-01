# https://medium.com/1mgofficial/how-to-override-uvicorn-logger-in-fastapi-using-loguru-124133cdcd4e

import sys
import logging

from pathlib import Path
from loguru import logger
from app.core.config import settings


class InterceptHandler(logging.Handler):
    def emit(self, record):
        level = record.levelname

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        log = logger.bind(request_id="app")
        log.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class CustomizeLogger:
    @classmethod
    def make_logger(cls):
        logger = cls.customize_logging(
            settings.logging_path,
            level=settings.logging_level,
            retention=settings.logging_retention,
            rotation=settings.logging_rotation,
            format=settings.logging_format,
        )
        return logger

    @classmethod
    def customize_logging(
        cls, filepath: Path, level: str, rotation: str, retention: str, format: str
    ):

        logger.remove()
        logger.add(
            sys.stdout,
            enqueue=True,
            backtrace=True,
            level=logging.getLevelName(level),
            format=format,
        )
        logger.add(
            str(filepath),
            rotation=rotation,
            retention=retention,
            enqueue=True,
            backtrace=True,
            level=logging.getLevelName(level),
            format=format,
        )
        logging.basicConfig(handlers=[InterceptHandler()], level=0)
        logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
        for _log in ["uvicorn", "uvicorn.error", "fastapi"]:
            _logger = logging.getLogger(_log)
            _logger.handlers = [InterceptHandler()]

        return logger.bind(request_id=None, method=None)


logger = CustomizeLogger.make_logger()
