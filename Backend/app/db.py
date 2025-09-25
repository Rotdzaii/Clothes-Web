# app/db.py
"""
Database configuration and helpers.

- Uses pydantic-settings (BaseSettings) to load environment variables.
- Accepts DB_ prefix variables: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME.
- Alternatively you can set DATABASE_URL (full DB URL) and it will be used directly.
- Provides:
    - engine: SQLAlchemy Engine
    - SessionLocal: session factory
    - Base: declarative base for models
    - get_db(): FastAPI dependency that yields a session
    - init_db(): helper to create tables (dev convenience)
"""

from typing import Iterator, Optional
import urllib.parse
import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

class Settings(BaseSettings):
    # Logical (snake_case) fields in code will be populated from env vars with prefix DB_
    db_user: str
    db_password: str
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str


    # Optional: full URL override (no prefix)
    database_url: Optional[str] = None

    # Pydantic-settings config: read from .env and map DB_ prefixed names to our fields
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DB_",   # DB_USER -> db_user, DB_PASSWORD -> db_password, ...
        extra="ignore",
    )

# Instantiate settings (reads .env)
settings = Settings()

def get_database_url() -> str:
    """
    Return a SQLAlchemy database URL.

    Priority:
      1. use settings.database_url if provided (explicit DATABASE_URL in .env or env)
      2. otherwise build from DB_* components
    """
    # If user provided an explicit DATABASE_URL (without DB_ prefix), prefer it
    env_db_url = os.getenv("DATABASE_URL") or settings.database_url
    if env_db_url:
        return env_db_url

    # Quote user/password to be safe with special chars
    user = urllib.parse.quote_plus(settings.db_user)
    password = urllib.parse.quote_plus(settings.db_password)
    host = settings.db_host
    port = settings.db_port
    name = settings.db_name

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"

# Create engine and session factory
DATABASE_URL = get_database_url()

# tune pool_size / max_overflow as needed for production
engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for models
Base = declarative_base()

# FastAPI dependency
def get_db() -> Iterator[sessionmaker]:
    """
    Yield a SQLAlchemy Session (for use with FastAPI Depends).
    Usage:
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dev helper: create tables from models (call carefully; prefer alembic in prod)
def init_db() -> None:
    """
    Create database tables from SQLAlchemy models (Base.metadata).
    For development only; in production use migrations (Alembic).
    """
    Base.metadata.create_all(bind=engine)


# Optional: small db-check helper used by a /dbcheck endpoint
def db_check() -> bool:
    """
    Quick raw DB check returning True if a simple SELECT 1 works.
    """
    try:
        with engine.connect() as conn:
            r = conn.execute("SELECT 1").scalar()
            return int(r) == 1
    except Exception:
        return False
