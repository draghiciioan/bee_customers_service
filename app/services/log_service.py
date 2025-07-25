import asyncio
import json
import urllib.request
from typing import Any, Dict

try:  # httpx may not be available in production
    import httpx
except Exception:  # pragma: no cover - optional dependency
    httpx = None

from app.core.config import settings


async def send_log(event: str, data: Dict[str, Any], trace_id: str) -> None:
    """Send a log entry to the external log service."""
    if not settings.LOG_SERVICE_URL:
        return

    payload = {"event": event, "data": data, "trace_id": trace_id}
    if httpx is not None:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(settings.LOG_SERVICE_URL, json=payload, timeout=2)
            return
        except Exception:  # pragma: no cover - network issues
            pass
    else:
        def post_log() -> None:
            req = urllib.request.Request(
                settings.LOG_SERVICE_URL,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=2)

        try:
            await asyncio.to_thread(post_log)
        except Exception:  # pragma: no cover - network issues
            pass


def send_log_sync(event: str, data: Dict[str, Any], trace_id: str) -> None:
    """Synchronous wrapper for :func:`send_log`."""
    try:
        asyncio.run(send_log(event, data, trace_id))
    except Exception:
        pass
