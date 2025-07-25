import asyncio
import json

import aio_pika
import redis

from app.core.config import settings


async def publish_event(event_name: str, payload: dict, trace_id: str) -> None:
    """Publish an event to RabbitMQ using aio_pika."""
    message_body = json.dumps(payload).encode()
    attempts = 0
    while attempts < 2:
        connection = None
        try:
            connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                settings.RABBITMQ_EXCHANGE,
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
            message = aio_pika.Message(
                body=message_body,
                content_type="application/json",
                headers={"trace_id": trace_id},
            )
            await exchange.publish(message, routing_key=event_name)
            break
        except Exception:
            attempts += 1
            if attempts >= 2:
                raise
            await asyncio.sleep(1)
        finally:
            if connection:
                await connection.close()


def _store_failed_event(event_name: str, payload: dict, trace_id: str) -> None:
    """Store failed event payload in Redis for later processing."""
    if not settings.REDIS_URL:
        return
    try:
        client = redis.from_url(settings.REDIS_URL)
        data = json.dumps({
            "event": event_name,
            "payload": payload,
            "trace_id": trace_id,
        })
        client.rpush("failed_events", data)
    except Exception:
        # Storing failures should not crash the app
        pass


def publish_event_sync(event_name: str, payload: dict, trace_id: str) -> None:
    """Synchronous wrapper for :func:`publish_event` with Redis backup."""
    try:
        asyncio.run(publish_event(event_name, payload, trace_id))
    except Exception:
        _store_failed_event(event_name, payload, trace_id)

