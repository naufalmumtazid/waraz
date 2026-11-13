"""Configuration and constants for Feature 2: Recycled Video Tracker.

Provides adjustable thresholds for keyframe extraction, perceptual hashing,
and sequential temporal matching.
"""

import os
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# Keyframe Extraction
# ─────────────────────────────────────────────────────────────

# Extraction interval in seconds (default: 1 keyframe every 2 seconds)
FRAME_INTERVAL_SECONDS: float = 2.0

# ─────────────────────────────────────────────────────────────
# Perceptual Hashing
# ─────────────────────────────────────────────────────────────

# Hash dimension (pHash default = 64-bit represented as 16-char hex)
HASH_SIZE: int = 8

# ─────────────────────────────────────────────────────────────
# Matching & Sequence Verification
# ─────────────────────────────────────────────────────────────

# Hamming distance threshold: frames are considered matching if distance <= threshold
HAMMING_THRESHOLD: int = 10

# Minimum consecutive matching frames required to verify recycled footage
MIN_CONSECUTIVE_FRAMES: int = 3

# ─────────────────────────────────────────────────────────────
# Output Statuses
# ─────────────────────────────────────────────────────────────

STATUS_RECYCLED = "kemungkinan_daur_ulang"
STATUS_NOT_FOUND = "tidak_ditemukan_di_arsip"
STATUS_UNPROCESSABLE = "tidak_dapat_diproses"

# Confidence thresholds
CONFIDENCE_HIGH_THRESHOLD: float = 0.75
CONFIDENCE_MEDIUM_THRESHOLD: float = 0.40

# ─────────────────────────────────────────────────────────────
# Storage Directories
# ─────────────────────────────────────────────────────────────

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


def _resolve_data_dir() -> Path:
    """Return a writable directory for local runs or Vercel serverless deployments."""
    if os.environ.get("VERCEL"):
        return Path("/tmp/data")
    return _BACKEND_DIR / "data"


DATA_DIR = _resolve_data_dir()
THUMBNAIL_DIR = DATA_DIR / "thumbnails"
VIDEO_ARCHIVE_DIR = DATA_DIR / "arsip_video"
TEMP_DIR = DATA_DIR / "temp"


def ensure_storage_dirs() -> tuple[Path, Path, Path, Path]:
    """Create storage directories lazily only when they are needed."""
    base_dir = _resolve_data_dir()
    dirs = (
        base_dir,
        base_dir / "thumbnails",
        base_dir / "arsip_video",
        base_dir / "temp",
    )
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
    return dirs

# ─────────────────────────────────────────────────────────────
# Backward-compatibility Aliases
# ─────────────────────────────────────────────────────────────
INTERVAL_DETIK = FRAME_INTERVAL_SECONDS
AMBANG_HAMMING = HAMMING_THRESHOLD
MIN_BERURUTAN = MIN_CONSECUTIVE_FRAMES
STATUS_DAUR_ULANG = STATUS_RECYCLED
STATUS_TIDAK_DITEMUKAN = STATUS_NOT_FOUND
STATUS_TIDAK_DAPAT_DIPROSES = STATUS_UNPROCESSABLE
AMBANG_KEYAKINAN_TINGGI = CONFIDENCE_HIGH_THRESHOLD
AMBANG_KEYAKINAN_SEDANG = CONFIDENCE_MEDIUM_THRESHOLD
ARSIP_VIDEO_DIR = VIDEO_ARCHIVE_DIR
