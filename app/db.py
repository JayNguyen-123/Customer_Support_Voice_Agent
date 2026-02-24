import asyncio
import logging
from typing import Optional
import asyncpg
# from .config import settings # Assuming settings are defined elsewhere

# Mock settings for demonstration purposes
class Settings:
    db_host = "localhost"
    db_name = "testdb"
    db_user = "testuser"
    db_password = "testpassword"
    db_min_conn = 1
    db_max_conn = 10

settings = Settings()

logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None

async def init_db_pool():
    global _pool
    if _pool is None:
        for attempt in range(5):
            try:
                _pool = await asyncpg.create_pool( # Removed the trailing comma here
                    host=settings.db_host,
                    database=settings.db_name,
                    user=settings.db_user,
                    password=settings.db_password,
                    min_size=settings.db_min_conn,
                    max_size=settings.db_max_conn,
                ) # The comma was here
                logger.info("DB pool initialized")
                break
            except Exception as e:
                logger.error(f"DB connection attempt {attempt+1} failed: {e}")
                await asyncio.sleep(2)
        if _pool is None:
            raise RuntimeError("Failed to initialized DB pool")

async def lookup_order(order_id: str) -> dict:
    # It's better practice to ensure pool is initialized before calling this function
    if _pool is None:
        await init_db_pool()
    async with _pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT order_id, status, carrier, tracking_number, estimated_delivery
            FROM orders
            WHERE order_id = $1
            """,
            order_id,
        )

        if not row:
            # Consistent formatting for the error message
            return {"error": f"Order {order_id} not found"}
        return dict(row)
