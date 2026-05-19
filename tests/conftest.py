"""
Shared pytest fixtures.

Uses an in-memory SQLite database so tests never need a running Postgres
instance.  SQLModel/SQLAlchemy treat SQLite and Postgres identically for
the operations we care about here.
"""

import io
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel

from app.database import get_session
from app.main import create_app


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

@pytest.fixture(name="engine", scope="function")
async def engine_fixture():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture(name="session", scope="function")
async def session_fixture(engine):
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as session:
        yield session


@pytest.fixture(name="client", scope="function")
def client_fixture(engine):
    from contextlib import asynccontextmanager
    from sqlalchemy.ext.asyncio import async_sessionmaker
    from sqlmodel.ext.asyncio.session import AsyncSession

    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    @asynccontextmanager
    async def noop_lifespan(app):
        yield

    app = create_app()
    app.router.lifespan_context = noop_lifespan

    async def override_session():
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_session

    with TestClient(app) as client:
        yield client

# ── File helpers ──────────────────────────────────────────────────────────────

def make_file(content: bytes, filename: str = "test.txt"):
    """Return a (field_name, (filename, file-like, mime)) tuple for multipart upload."""
    return ("file", (filename, io.BytesIO(content), "application/octet-stream"))
