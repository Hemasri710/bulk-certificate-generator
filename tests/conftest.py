import sys
import shutil
import pytest
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
settings.DATABASE_URL = "sqlite:///:memory:"

import app.main as app_main
from app.main import app
from app.core.database import Base, get_db

# In-memory SQLite DB for fast, isolated testing
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Patch main app engine so lifespan creates tables on the test in-memory SQLite DB
app_main.engine = engine


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(tmp_path_factory):
    """Sets up a temporary storage directory for tests."""
    temp_dir = tmp_path_factory.mktemp("test_certificates")
    settings.STORAGE_DIR = temp_dir
    yield
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def db_session(monkeypatch):
    """Creates a fresh database session for each test function and patches background worker session maker."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Patch SessionLocal in job_service so background tasks use TestingSessionLocal
    monkeypatch.setattr("app.services.job_service.SessionLocal", TestingSessionLocal)
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
