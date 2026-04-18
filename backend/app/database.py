import os
from typing import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./maintainx.db")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)


# SQLite needs PRAGMA foreign_keys=ON per connection or ON DELETE CASCADE is a no-op.
@event.listens_for(engine.sync_engine, "connect")
def _enable_sqlite_fk(dbapi_connection, _):
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    from app import models  # noqa: F401  ensure models register with Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
