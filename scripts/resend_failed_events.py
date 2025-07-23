import json
import redis

from app.core.config import settings
from app.services.event_publisher import publish_event_sync


def resend_failed_events() -> None:
    """Resend events stored in Redis failed_events list."""
    if not settings.REDIS_URL:
        return
    client = redis.from_url(settings.REDIS_URL)
    while True:
        data = client.lpop("failed_events")
        if data is None:
            break
        try:
            event = json.loads(data)
            publish_event_sync(event["event"], event["payload"], event["trace_id"])
        except Exception:
            client.rpush("failed_events", data)
            break


if __name__ == "__main__":
    resend_failed_events()
