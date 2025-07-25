import asyncio
from app.db.database import engine

async def test_connection():
    """Test that we can connect to the database with the async engine."""
    try:
        # Try to connect to the database
        conn = await engine.connect()
        print("Successfully connected to the database!")
        await conn.close()
        return True
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())