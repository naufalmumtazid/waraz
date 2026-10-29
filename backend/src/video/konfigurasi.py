"""Konfigurasi dan konstanta untuk Fitur 2: Pelacak Video Daur Ulang.

Semua ambang batas disimpan di sini agar mudah diatur.
Sesuai agent.md bagian 8, F2.
"""

# ──────────────────────────────────────────────
# Ekstraksi Frame
# ──────────────────────────────────────────────

# Interval ekstraksi keyframe (detik)
INTERVAL_DETIK: float = 2.0

# ──────────────────────────────────────────────
# Hashing
# ──────────────────────────────────────────────

# Ukuran hash (bit). pHash default = 64-bit (8x8)
HASH_SIZE: int = 8

# ──────────────────────────────────────────────
# Pencocokan
# ──────────────────────────────────────────────

# Ambang jarak Hamming: frame dianggap cocok jika jarak <= AMBANG_HAMMING
AMBANG_HAMMING: int = 10

# Minimum frame berurutan yang harus cocok agar video dinyatakan "daur ulang"
MIN_BERURUTAN: int = 3

# ──────────────────────────────────────────────
# Status hasil
# ──────────────────────────────────────────────

STATUS_DAUR_ULANG = "kemungkinan_daur_ulang"
STATUS_TIDAK_DITEMUKAN = "tidak_ditemukan_di_arsip"
STATUS_TIDAK_DAPAT_DIPROSES = "tidak_dapat_diproses"

# ──────────────────────────────────────────────
# Keyakinan
# ──────────────────────────────────────────────

# Threshold skor untuk menentukan tingkat keyakinan
AMBANG_KEYAKINAN_TINGGI: float = 0.75
AMBANG_KEYAKINAN_SEDANG: float = 0.40

# ──────────────────────────────────────────────
# Path
# ──────────────────────────────────────────────

import os
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = _BACKEND_DIR / "data"
THUMBNAIL_DIR = DATA_DIR / "thumbnails"
ARSIP_VIDEO_DIR = DATA_DIR / "arsip_video"
TEMP_DIR = DATA_DIR / "temp"

# Pastikan direktori ada
for _d in [DATA_DIR, THUMBNAIL_DIR, ARSIP_VIDEO_DIR, TEMP_DIR]:
    _d.mkdir(parents=True, exist_ok=True)
