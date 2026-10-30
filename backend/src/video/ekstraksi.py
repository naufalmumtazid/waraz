"""Backward-compatibility layer for video extraction.

Delegates to `src.video.extraction` with Indonesian parameter aliases.
"""

from .extraction import (
    VideoExtractionError,
    get_video_info,
    extract_keyframes,
    save_thumbnail,
)
from typing import Any, Dict, List
from pathlib import Path


def dapatkan_info_video(video_path) -> Dict[str, Any]:
    """Indonesian alias for get_video_info."""
    return get_video_info(video_path)


def ekstrak_frame(
    video_path,
    interval_detik: float = None,
    interval_seconds: float = None,
) -> List[Dict[str, Any]]:
    """Indonesian alias for extract_keyframes.

    Accepts both ``interval_detik`` (Indonesian) and ``interval_seconds`` (English).
    """
    from .config import FRAME_INTERVAL_SECONDS
    interval = interval_detik if interval_detik is not None else (
        interval_seconds if interval_seconds is not None else FRAME_INTERVAL_SECONDS
    )
    return extract_keyframes(video_path, interval_seconds=interval)


def simpan_thumbnail(frame_image, video_id: str, frame_index: int) -> str:
    """Indonesian alias for save_thumbnail."""
    return save_thumbnail(frame_image, video_id, frame_index)


__all__ = [
    "VideoExtractionError",
    "get_video_info",
    "dapatkan_info_video",
    "extract_keyframes",
    "ekstrak_frame",
    "save_thumbnail",
    "simpan_thumbnail",
]
