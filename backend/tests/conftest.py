"""
Shared pytest fixtures for the backend test suite.

IMPORTANT: app.config.Settings() reads required env vars (DATABASE_URL,
SECRET_KEY) at *import time* via the module-level `settings = get_settings()`
line. That means these env vars must be set before anything under `app.*`
is imported for the first time — hence they're set here, at the very top of
conftest.py, before the `from app...` imports below.
"""

import os
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite:///./tests/test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-do-not-use-in-production")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DEBUG", "False")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000")
os.environ.setdefault("UPLOAD_DIR", "./tests/uploads")

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.dependencies import get_db
from app.main import app

TEST_DB_PATH = Path(__file__).parent / "test.db"

engine = create_engine(
    f"sqlite:///{TEST_DB_PATH}",
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Swap the real (SQLite/Postgres) DB dependency for the isolated test DB for
# every route in the app, for the whole test session.
app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(scope="session", autouse=True)
def _test_database():
    """Create all tables once per test run, drop them and remove the file after."""
    # Import models so they register on Base.metadata before create_all.
    from app.models import documents, job_application, user  # noqa: F401

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture
async def client():
    """An httpx.AsyncClient wired directly to the FastAPI app (no network)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
