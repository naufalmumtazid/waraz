"""pytest configuration for WARAZ backend tests.

Forces SQLite for all tests so the suite runs offline without Supabase.
Must run before any modules that call load_dotenv() so DATABASE_URL
resolves to empty and connection.py falls back to local SQLite.
"""

import os

# Set DATABASE_URL to empty string *before* any module imports load_dotenv().
# dotenv's load_dotenv() will NOT overwrite existing env vars by default
# (override=False), so this empty string takes precedence.
os.environ["DATABASE_URL"] = ""
os.environ.pop("SUPABASE_DATABASE_URL", None)
