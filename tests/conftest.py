import os
import importlib
import sys
import uuid
import asyncio

import pytest
import pytest_asyncio
import jwt
import httpx

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

from app.core.config import settings

from app.db import database
from app.db.database import Base


@pytest.fixture(scope="function")
def db_session(tmp_path):
    db_path = tmp_path / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
    importlib.reload(database)
    for mod in ["app.models.customer", "app.models.customer_tag", "app.services.tag_service"]:
        if mod in sys.modules:
            del sys.modules[mod]
    import app.models.customer  # noqa: F401
    import app.models.customer_tag  # noqa: F401
    import app.services.tag_service  # noqa: F401

    async def reset_db():
        async with database.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(reset_db())
    session = database.SessionLocal()
    try:
        yield session
    finally:
        # Ensure the async session is properly closed to avoid warnings
        asyncio.run(session.close())


@pytest.fixture()
def auth_headers():
    token = jwt.encode(
        {"sub": str(uuid.uuid4()), "role": "admin_business"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def internal_headers():
    token = jwt.encode(
        {"sub": str(uuid.uuid4()), "role": "internal"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def disable_event_publisher(monkeypatch, request):
    if "test_event_publisher" in str(request.fspath):
        return
    async def dummy_publish(event_name: str, payload: dict, trace_id: str):
        return None

    monkeypatch.setattr(
        "app.services.event_publisher.publish_event", dummy_publish
    )

    original_async_patch = httpx.AsyncClient.patch

    async def async_patch(self, url, *args, **kwargs):
        if url.startswith(settings.AUTH_SERVICE_URL):
            return httpx.patch(url, *args, **kwargs)
        return await original_async_patch(self, url, *args, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "patch", async_patch)


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session, monkeypatch):
    db_path = db_session.bind.url.database
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
    importlib.reload(database)
    import main
    importlib.reload(main)
    from main import app

    async def dummy_publish(event_name: str, payload: dict, trace_id: str):
        return None

    monkeypatch.setattr(
        "app.services.event_publisher.publish_event", dummy_publish
    )

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[database.get_db] = override_get_db

    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()


