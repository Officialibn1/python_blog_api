import logging
from datetime import datetime, timezone
from fastapi import Request
from pythonjsonlogger.json import JsonFormatter

def setup_logging() -> logging.Logger:
    logger = logging.getLogger("blog_api")
    logger.setLevel(logging.INFO)

    log_handler = logging.StreamHandler()
    formatter = JsonFormatter("{message}{asctime}{exc_info}", style="{")
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    return logger

logger = setup_logging()

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"blog_api.{name}")

async def logging_middleware(request: Request, call_next):
    start = datetime.now(timezone.utc)
    response = await call_next(request)
    duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000

    logger.info(
        "request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration, 2)
        }
    )

    return response
