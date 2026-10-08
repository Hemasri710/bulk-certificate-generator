import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger("app.core.database")

def create_db_engine():
    db_url = settings.DATABASE_URL
    connect_args = {}
    
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        return create_engine(db_url, connect_args=connect_args, pool_pre_ping=True)

    try:
        eng = create_engine(db_url, connect_args=connect_args, pool_pre_ping=True)
        # Verify connection
        with eng.connect() as conn:
            pass
        return eng
    except Exception as e:
        logger.warning(
            f"Could not connect to configured database at '{db_url}': {str(e)}. "
            "Falling back to local SQLite database (sqlite:///./certificates.db) for local development."
        )
        sqlite_url = "sqlite:///./certificates.db"
        return create_engine(sqlite_url, connect_args={"check_same_thread": False}, pool_pre_ping=True)

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a database session for API endpoints.

    Ensures session is closed cleanly after request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
