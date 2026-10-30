"""Backward-compatibility layer for video service.

Delegates directly to `src.video.service`.
"""

from .service import (
    daftarkan_video_arsip,
    delete_archive_video,
    dapatkan_daftar_arsip,
    detect_recycled_video,
    deteksi_video_daur_ulang,
    get_archive_list,
    hapus_video_arsip,
    register_video_archive,
)

__all__ = [
    "register_video_archive",
    "daftarkan_video_arsip",
    "detect_recycled_video",
    "deteksi_video_daur_ulang",
    "get_archive_list",
    "dapatkan_daftar_arsip",
    "delete_archive_video",
    "hapus_video_arsip",
]
