"""Configuration for Feature 1: Issue Clarification.

Admin credentials and token are read from environment variables
(WARAZ_ADMIN_EMAIL, WARAZ_ADMIN_PASSWORD, WARAZ_ADMIN_TOKEN), typically
configured via backend/.env or the host environment.
"""

import os

# ─────────────────────────────────────────────────────────────
# Admin Access
# ─────────────────────────────────────────────────────────────

def get_admin_email() -> str:
    """Admin account email used by the login endpoint."""
    return os.getenv("WARAZ_ADMIN_EMAIL", "admin@waraz.local")


def get_admin_password() -> str:
    """Admin account password used by the login endpoint."""
    return os.getenv("WARAZ_ADMIN_PASSWORD", "waraz-admin-2026")


def get_admin_token() -> str:
    """Static bearer-ish token returned on successful admin login."""
    return os.getenv("WARAZ_ADMIN_TOKEN", "waraz-demo-admin-token")


# ─────────────────────────────────────────────────────────────
# Matching Thresholds
# ─────────────────────────────────────────────────────────────

# Normalized similarity >= CONFIRMED_THRESHOLD → "sudah_diklarifikasi"
CONFIRMED_THRESHOLD: float = 0.62

# Normalized similarity >= SIMILAR_THRESHOLD → "ditemukan_mirip"
SIMILAR_THRESHOLD: float = 0.34

# Maximum number of matches returned by /check
MAX_MATCHES: int = 5

# ─────────────────────────────────────────────────────────────
# Output Statuses
# ─────────────────────────────────────────────────────────────

STATUS_CLAIM = "menunggu"
STATUS_APPROVED = "disetujui"
STATUS_REJECTED = "ditolak"
