import asyncio
from typing import Any, Dict

import httpx

from app.core.config import settings


async def send_log(event: str, data: Dict[str, Any], trace_id: str) -> None:
    """Send a log entry to the external log service."""
    if not settings.LOG_SERVICE_URL:
        return

    payload = {"event": event, "data": data, "trace_id": trace_id}
    try:
        async with httpx.AsyncClient() as client:
            await client.post(settings.LOG_SERVICE_URL, json=payload, timeout=2)
    except Exception:
        # Logging should not interrupt the main workflow
        pass


def send_log_sync(event: str, data: Dict[str, Any], trace_id: str) -> None:
    """Synchronous wrapper for :func:`send_log`."""
    try:
        asyncio.run(send_log(event, data, trace_id))
    except Exception:
        pass
