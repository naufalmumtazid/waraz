"""Backward-compatibility layer for video extraction.

Delegates directly to `src.video.extraction`.
"""

from .extraction import (
    VideoExtractionError,
    dapatkan_info_video,
    ekstrak_frame,
    extract_keyframes,
    get_video_info,
    save_thumbnail,
    simpan_thumbnail,
)

__all__ = [
    "VideoExtractionError",
    "get_video_info",
    "dapatkan_info_video",
    "extract_keyframes",
    "ekstrak_frame",
    "save_thumbnail",
    "simpan_thumbnail",
]
