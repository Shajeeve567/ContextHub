from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.event import listens_for
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from api.app.core.config import settings


def _build_async_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if database_url.startswith("sqlite+aiosqlite://"):
        return database_url
    if database_url.startswith("sqlite:///"):
        return database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return database_url


async_database_url = _build_async_database_url(settings.DATABASE_URL)

engine = create_async_engine(async_database_url, echo=False)

# Run pgvector initialization on first connection
@listens_for(engine.sync_engine, "connect")
def run_on_connect(dbapi_connection, connection_record):
    """Executes code directly on the raw DBAPI connection when it is first created."""
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        dbapi_connection.commit()
    except Exception:
        dbapi_connection.rollback()
        raise
    finally:
        cursor.close()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


async def init_db() -> None:
    async with engine.begin() as connection:
        # The connection event above will trigger right before metadata creation runs
        await connection.run_sync(Base.metadata.create_all)
