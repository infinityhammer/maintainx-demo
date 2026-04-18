import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ.setdefault("APP_ENV", "test")

from app import database  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    # Per-test in-memory engine — guarantees isolation between tests.
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine.sync_engine, "connect")
    def _enable_sqlite_fk(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    TestSession = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with TestSession() as session:
            yield session

    # Patch the lifespan-driven init_db so the app does not try to talk to the
    # production database when the ASGI lifespan starts.
    async def noop_init_db():
        return None

    original_init_db = database.init_db
    database.init_db = noop_init_db
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    database.init_db = original_init_db
    await engine.dispose()


@pytest_asyncio.fixture
async def sample_aircraft(client: AsyncClient) -> dict:
    payload = {
        "tail_number": "F-35A-001",
        "model": "F-35A Lightning II",
        "squadron": "388th Fighter Wing",
        "status": "operational",
    }
    resp = await client.post("/aircraft", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest_asyncio.fixture
async def sample_work_order(client: AsyncClient, sample_aircraft: dict) -> dict:
    payload = {
        "aircraft_id": sample_aircraft["id"],
        "title": "Replace hydraulic line",
        "description": "Port-side main hydraulic line shows fatigue cracks.",
        "priority": "high",
        "status": "open",
    }
    resp = await client.post("/work-orders", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()
