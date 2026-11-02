"""Database and PostgreSQL (Neon/Supabase) connection management for WARAZ.

Supports PostgreSQL (Neon / Supabase) for production/serverless deployments
and local SQLite for offline development and local testing.
"""

import logging
import os
from pathlib import Path
from typing import Generator, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

# Load environment variables from .env if present
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(_BACKEND_DIR / ".env")

logger = logging.getLogger("waraz.db")

# ─────────────────────────────────────────────────────────────
# Database URL Resolution (Cloud PostgreSQL vs SQLite fallback)
# ─────────────────────────────────────────────────────────────

RAW_DB_URL = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DATABASE_URL")

if RAW_DB_URL:
    # Ensure standard postgresql:// scheme for SQLAlchemy compatibility
    if RAW_DB_URL.startswith("postgres://"):
        DATABASE_URL = RAW_DB_URL.replace("postgres://", "postgresql://", 1)
    else:
        DATABASE_URL = RAW_DB_URL
    IS_SQLITE = False
    logger.info("Configuring PostgreSQL (Neon/Cloud) database engine.")
else:
    # Local SQLite fallback for development & offline testing
    _DATA_DIR = _BACKEND_DIR / "data"
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH = _DATA_DIR / "waraz.db"
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    IS_SQLITE = True
    logger.info("DATABASE_URL not set. Falling back to local SQLite at %s", DB_PATH)

# Engine configuration
if IS_SQLITE:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()

else:
    # PostgreSQL connection (Neon / Cloud)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency provider for FastAPI / application database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(target_engine: Optional[Engine] = None):
    """Creates all database tables defined in models if they don't already exist."""
    from .models import Base
    eng = target_engine or engine
    Base.metadata.create_all(bind=eng)
    db_type = "SQLite" if IS_SQLITE else "PostgreSQL (Neon/Cloud)"
    print(f"[DB] {db_type} database initialized successfully.")



# ─────────────────────────────────────────────────────────────
# Supabase SDK Client Helper (Optional API / Storage access)
# ─────────────────────────────────────────────────────────────

_supabase_client = None


def get_supabase_client():
    """Returns initialized Supabase Client if credentials are provided."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if supabase_url and supabase_key:
        try:
            from supabase import create_client
            _supabase_client = create_client(supabase_url, supabase_key)
            logger.info("Connected to Supabase client at %s", supabase_url)
            return _supabase_client
        except Exception as e:
            logger.warning("Failed to initialize Supabase client: %s", e)
            return None
    return None
