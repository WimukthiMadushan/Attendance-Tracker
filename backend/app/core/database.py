"""
Database client module with PostgreSQL connection pooling.
Provides:
1. High-performance asynchronous connection pooling via asyncpg.
2. Direct connection pool helpers (fetch, fetchrow, fetchval, execute, executemany, transaction).
3. ORM integration via Prisma Python client.
4. FastAPI dependency injection and lifecycle hooks (connect_db, disconnect_db).
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import asyncpg
from app.core.config import settings

logger = logging.getLogger("task_tracker.db")


def _sanitize_dsn(database_url: str) -> tuple[str, Optional[str]]:
    """
    Parse DATABASE_URL and extract clean DSN and search_path schema.
    Prisma often appends ?schema=public which asyncpg rejects in the DSN.
    """
    parsed = urlparse(database_url)
    clean_dsn = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    query_params = parse_qs(parsed.query)
    schema = query_params.get("schema", [None])[0]
    return clean_dsn, schema


class DatabaseClient:
    """
    PostgreSQL Database Client with managed async connection pooling.
    """

    def __init__(
        self,
        min_size: int = 5,
        max_size: int = 20,
        max_inactive_connection_lifetime: float = 300.0,
        command_timeout: float = 60.0,
    ):
        self.min_size = min_size
        self.max_size = max_size
        self.max_inactive_connection_lifetime = max_inactive_connection_lifetime
        self.command_timeout = command_timeout
        self.pool: Optional[asyncpg.Pool] = None
        self._is_connecting = False

    async def connect(self, dsn: Optional[str] = None) -> None:
        """Initialize the connection pool."""
        if self.pool is not None and not self.pool._closed:
            return

        db_url = dsn or settings.DATABASE_URL
        clean_dsn, schema = _sanitize_dsn(db_url)
        server_settings = {"search_path": schema} if schema else {}

        try:
            logger.info("Initializing PostgreSQL connection pool...")
            self.pool = await asyncpg.create_pool(
                clean_dsn,
                min_size=self.min_size,
                max_size=self.max_size,
                max_inactive_connection_lifetime=self.max_inactive_connection_lifetime,
                command_timeout=self.command_timeout,
                server_settings=server_settings,
            )
            logger.info(
                f"PostgreSQL connection pool established (min={self.min_size}, max={self.max_size})."
            )
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL connection pool: {e}")
            raise

    async def disconnect(self) -> None:
        """Gracefully close all connections in the pool."""
        if self.pool is not None:
            logger.info("Closing PostgreSQL connection pool...")
            await self.pool.close()
            self.pool = None
            logger.info("PostgreSQL connection pool closed.")

    @property
    def is_connected(self) -> bool:
        return self.pool is not None and not self.pool._closed

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Context manager to acquire and safely release a connection from the pool."""
        if self.pool is None or self.pool._closed:
            raise RuntimeError("Database connection pool is not connected.")
        async with self.pool.acquire() as conn:
            yield conn

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Context manager to execute queries within an atomic transaction."""
        async with self.connection() as conn:
            async with conn.transaction():
                yield conn

    async def fetch(self, query: str, *args: Any) -> List[asyncpg.Record]:
        """Fetch multiple rows matching query."""
        async with self.connection() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args: Any) -> Optional[asyncpg.Record]:
        """Fetch a single row matching query."""
        async with self.connection() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args: Any) -> Any:
        """Fetch a single scalar value."""
        async with self.connection() as conn:
            return await conn.fetchval(query, *args)

    async def execute(self, query: str, *args: Any) -> str:
        """Execute a query without returning rows."""
        async with self.connection() as conn:
            return await conn.execute(query, *args)

    async def executemany(self, query: str, args: List[Any]) -> None:
        """Execute a query for each parameter sequence in args."""
        async with self.connection() as conn:
            await conn.executemany(query, args)

    async def health_check(self) -> Dict[str, Any]:
        """Ping database and return pool connection statistics."""
        if not self.is_connected:
            return {"status": "unhealthy", "error": "Pool not initialized"}
        try:
            val = await self.fetchval("SELECT 1")
            return {
                "status": "healthy" if val == 1 else "degraded",
                "pool_size": self.pool.get_size(),
                "free_connections": self.pool.get_idle_size(),
                "min_size": self.min_size,
                "max_size": self.max_size,
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Global database pool instance
db_client = DatabaseClient()

# Prisma Client initialization with fallback
try:
    from prisma import Prisma

    prisma_client: Optional[Prisma] = Prisma(auto_register=True)
except (ImportError, RuntimeError, Exception) as e:
    prisma_client = None
    logger.warning(
        f"Prisma client is not yet initialized ({e}). Run prisma generate to build it."
    )


async def connect_db() -> None:
    """Connect asyncpg pool and Prisma client on application startup."""
    # 1. Connect asyncpg pool
    try:
        await db_client.connect()
    except Exception as e:
        logger.warning(f"Connection pool initial connection failed: {e}")

    # 2. Connect Prisma client
    global prisma_client
    if prisma_client is not None and not prisma_client.is_connected():
        try:
            await prisma_client.connect()
            logger.info("Connected to PostgreSQL via Prisma ORM.")
        except Exception as e:
            logger.warning(f"Prisma ORM connection offline: {e}")


async def disconnect_db() -> None:
    """Close asyncpg pool and Prisma client on application shutdown."""
    # 1. Disconnect Prisma
    global prisma_client
    if prisma_client is not None and prisma_client.is_connected():
        try:
            await prisma_client.disconnect()
            logger.info("Prisma ORM disconnected.")
        except Exception as e:
            logger.error(f"Error disconnecting Prisma: {e}")

    # 2. Close asyncpg pool
    await db_client.disconnect()


def get_pool() -> DatabaseClient:
    """Dependency injection helper for the pooled database client."""
    return db_client


def get_prisma() -> Optional["Prisma"]:
    """Dependency injection helper for Prisma ORM."""
    if prisma_client is not None and prisma_client.is_connected():
        return prisma_client
    return None


def get_db():
    """Backward compatibility helper for existing service endpoints."""
    if prisma_client is not None and prisma_client.is_connected():
        return prisma_client
    return db_client
