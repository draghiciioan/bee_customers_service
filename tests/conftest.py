import os
import importlib
import sys
import pytest
import pytest_asyncio

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from app.db import database
from app.db.database import Base


@pytest.fixture(scope="function")
def db_session(tmp_path):
    db_path = tmp_path / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    importlib.reload(database)
    for mod in ["app.models.customer", "app.models.customer_tag", "app.services.tag_service"]:
        if mod in sys.modules:
            del sys.modules[mod]
    import app.models.customer  # noqa: F401
    import app.models.customer_tag  # noqa: F401
    import app.services.tag_service  # noqa: F401
    Base.metadata.drop_all(bind=database.engine)
    Base.metadata.create_all(bind=database.engine)
    session = database.SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session):
    os.environ["DATABASE_URL"] = db_session.bind.url.render_as_string(hide_password=False)
    importlib.reload(database)
    import main
    importlib.reload(main)
    from main import app

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


