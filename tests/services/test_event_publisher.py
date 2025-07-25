import json

import pytest
import aio_pika

from app.services.event_publisher import publish_event
from app.core.config import settings


@pytest.mark.asyncio
async def test_publish_event(monkeypatch):
    published = {}

    class DummyExchange:
        async def publish(self, message: aio_pika.Message, routing_key: str):
            published["routing_key"] = routing_key
            published["body"] = message.body.decode()

    class DummyChannel:
        async def declare_exchange(self, name: str, type: aio_pika.ExchangeType, durable: bool = True):
            assert name == settings.RABBITMQ_EXCHANGE
            return DummyExchange()

    class DummyConnection:
        async def channel(self):
            return DummyChannel()

        async def close(self):
            published["closed"] = True

    async def dummy_connect(url: str):
        assert url == settings.RABBITMQ_URL
        return DummyConnection()

    monkeypatch.setattr(aio_pika, "connect_robust", dummy_connect)

    await publish_event("test.event", {"foo": "bar"}, "trace")

    assert published["routing_key"] == "test.event"
    assert published["body"] == json.dumps({"foo": "bar"})
    assert published["closed"] is True


def test_publish_event_failure_stored(monkeypatch):
    stored = []

    class DummyRedis:
        def rpush(self, key, value):
            stored.append((key, value))

    monkeypatch.setattr("redis.from_url", lambda url: DummyRedis())

    async def dummy_connect(url: str):
        raise Exception("connection failed")

    monkeypatch.setattr(aio_pika, "connect_robust", dummy_connect)

    from app.services.event_publisher import publish_event_sync

    publish_event_sync("fail.event", {"foo": "bar"}, "trace123")

    assert stored
    key, value = stored[0]
    assert key == "failed_events"
    data = json.loads(value)
    assert data["event"] == "fail.event"
    assert data["payload"] == {"foo": "bar"}
    assert data["trace_id"] == "trace123"
