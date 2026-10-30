"""Video keyframe extraction module for Feature 2: Recycled Video Tracker.

Uses OpenCV (cv2) to read video files and extract keyframes at regular intervals
without requiring external ffmpeg binary binaries.
Converts extracted frames to RGB and PIL Image objects for perceptual hashing.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from .config import FRAME_INTERVAL_SECONDS, THUMBNAIL_DIR

logger = logging.getLogger("waraz.video.extraction")


class VideoExtractionError(Exception):
    """Raised when an error occurs while opening or decoding a video."""
    pass


def get_video_info(video_path: str | Path) -> Dict[str, Any]:
    """Retrieves basic video metadata (duration, fps, total frames, resolution).

    Args:
        video_path: Path to the video file.

    Returns:
        Dict with duration_seconds, fps, total_frames, width, height.
    """
    path_str = str(video_path)
    cap = cv2.VideoCapture(path_str)
    if not cap.isOpened():
        raise VideoExtractionError(f"Failed to open video file: {path_str}")

    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        lebar = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        tinggi = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        durasi = total_frame / fps if fps > 0 else 0.0

        return {
            "fps": round(fps, 2),
            "total_frame": total_frame,
            "durasi_detik": round(durasi, 2),
            "lebar": lebar,
            "tinggi": tinggi,
        }
    finally:
        cap.release()
        del cap


def extract_keyframes(
    video_path: str | Path,
    interval_seconds: float = FRAME_INTERVAL_SECONDS,
) -> List[Dict[str, Any]]:
    """Extracts keyframes from a video file at a specified interval.

    Args:
        video_path: Path to the video file.
        interval_seconds: Interval in seconds between extracted frames.

    Returns:
        List of dicts containing:
            - urutan: frame index (0-based)
            - detik: timestamp in seconds
            - image: PIL.Image object (RGB)
    """
    path_str = str(video_path)
    cap = cv2.VideoCapture(path_str)
    if not cap.isOpened():
        raise VideoExtractionError(f"Failed to open video file: {path_str}")

    results: List[Dict[str, Any]] = []

    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frame / fps if fps > 0 else 0.0

        if duration <= 0 or total_frame <= 0:
            success, frame_bgr = cap.read()
            if success and frame_bgr is not None:
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                results.append({
                    "urutan": 0,
                    "detik": 0.0,
                    "image": Image.fromarray(frame_rgb),
                })
            return results

        target_sec = 0.0
        seq = 0

        while target_sec <= duration:
            target_msec = target_sec * 1000.0
            cap.set(cv2.CAP_PROP_POS_MSEC, target_msec)
            success, frame_bgr = cap.read()

            if not success or frame_bgr is None:
                break

            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            results.append({
                "urutan": seq,
                "detik": round(target_sec, 2),
                "image": Image.fromarray(frame_rgb),
            })

            seq += 1
            target_sec += interval_seconds

        # Fallback for very short clips (< interval)
        if not results:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame_bgr = cap.read()
            if success and frame_bgr is not None:
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                results.append({
                    "urutan": 0,
                    "detik": 0.0,
                    "image": Image.fromarray(frame_rgb),
                })

        return results

    finally:
        cap.release()
        del cap


def save_thumbnail(
    image: Image.Image,
    output_path: str | Path,
    max_size: Tuple[int, int] = (320, 240),
) -> Path:
    """Saves a resized thumbnail image preserving aspect ratio."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    img_copy = image.copy()
    img_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
    img_copy.save(path, format="JPEG", quality=85)
    return path


# Backward compatibility
dapatkan_info_video = get_video_info
ekstrak_frame = extract_keyframes
simpan_thumbnail = save_thumbnail
