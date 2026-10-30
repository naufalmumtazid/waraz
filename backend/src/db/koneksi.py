"""Backward-compatibility layer for database connection.

Delegates directly to `src.db.connection`.
"""

from .connection import (
    DATABASE_URL,
    IS_SQLITE,
    SessionLocal,
    engine,
    get_db,
    get_supabase_client,
    init_db,
)

__all__ = [
    "DATABASE_URL",
    "IS_SQLITE",
    "SessionLocal",
    "engine",
    "get_db",
    "init_db",
    "get_supabase_client",
]
