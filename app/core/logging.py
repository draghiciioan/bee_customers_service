import json
import logging
from typing import Any, Dict

from app.core.config import settings


class JsonFormatter(logging.Formatter):
    """Format logs as structured JSON."""

    def __init__(self) -> None:
        super().__init__(datefmt="%Y-%m-%dT%H:%M:%S%z")

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        log_record: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname.lower(),
            "service_name": settings.PROJECT_NAME,
            "message": record.getMessage(),
        }

        if hasattr(record, "trace_id"):
            log_record["trace_id"] = record.trace_id

        # Include any custom extra attributes
        for key, value in record.__dict__.items():
            if key not in log_record and key not in {
                "args",
                "msg",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
            }:
                log_record[key] = value

        return json.dumps(log_record)


def setup_logging() -> None:
    """Configure root logger with :class:`JsonFormatter`."""

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)
