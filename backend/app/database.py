"""
NBK Salary API - Database Configuration

Synchronous SQLAlchemy setup with psycopg2-binary driver.
Provides engine, session factory, declarative base, and FastAPI dependency.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Create synchronous SQLAlchemy engine
# Support Neon PostgreSQL (requires sslmode=require)
connect_args = {}
if "neon" in settings.DATABASE_URL or "render" in settings.DATABASE_URL:
    connect_args["sslmode"] = "require"

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args=connect_args,
)

# Session factory bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for ORM models
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
