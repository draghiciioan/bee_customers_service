import asyncio

import pytest

from app.db.database import engine


@pytest.mark.asyncio
async def test_connection() -> None:
    """Ensure the async engine connects without errors."""
    async with engine.connect() as conn:
        assert await conn.run_sync(lambda c: True)


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    asyncio.run(test_connection())