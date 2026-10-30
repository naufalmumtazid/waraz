"""Perceptual hashing module for Feature 2: Recycled Video Tracker.

Uses imagehash (pHash and dHash) to generate robust visual fingerprints
resilient against compression, resizing, and minor modifications.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import imagehash
from PIL import Image

from .config import FRAME_INTERVAL_SECONDS, HASH_SIZE, THUMBNAIL_DIR
from .extraction import extract_keyframes, get_video_info, save_thumbnail

logger = logging.getLogger("waraz.video.hashing")


def calculate_phash(image: Image.Image, hash_size: int = HASH_SIZE) -> str:
    """Computes Discrete Cosine Transform (DCT) based perceptual hash (pHash).

    Args:
        image: PIL Image object.
        hash_size: Hash dimension (default 8 -> 64-bit).

    Returns:
        Hexadecimal string (16 characters for 64-bit).
    """
    ph = imagehash.phash(image, hash_size=hash_size)
    return str(ph)


def calculate_dhash(image: Image.Image, hash_size: int = HASH_SIZE) -> str:
    """Computes gradient difference hash (dHash).

    Args:
        image: PIL Image object.
        hash_size: Hash dimension (default 8).

    Returns:
        Hexadecimal string.
    """
    dh = imagehash.dhash(image, hash_size=hash_size)
    return str(dh)


def hamming_distance(hash1: str, hash2: str) -> int:
    """Calculates bitwise Hamming distance between two hex hash strings.

    Distance 0 indicates perceptual identity.
    Distance <= 10 indicates mild compression or cropped recycling.
    """
    try:
        val1 = int(hash1, 16)
        val2 = int(hash2, 16)
        return bin(val1 ^ val2).count("1")
    except (ValueError, TypeError):
        return 64


def process_video_hashes(
    video_path: str | Path,
    interval_seconds: float = FRAME_INTERVAL_SECONDS,
    save_first_thumbnail: bool = False,
    thumbnail_path: Optional[str | Path] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Extracts keyframes and computes dual pHash & dHash for each frame."""
    path = Path(video_path)
    info_video = get_video_info(path)
    frames = extract_keyframes(path, interval_seconds=interval_seconds)

    hash_results: List[Dict[str, Any]] = []

    for item in frames:
        pil_img = item["image"]
        ph = calculate_phash(pil_img)
        dh = calculate_dhash(pil_img)

        hash_results.append({
            "urutan": item["urutan"],
            "detik": item["detik"],
            "phash": ph,
            "dhash": dh,
            "image": pil_img,
        })

    if save_first_thumbnail and hash_results:
        first_frame = hash_results[0]["image"]
        target_thumb = thumbnail_path or (THUMBNAIL_DIR / f"{path.stem}_thumb.jpg")
        save_thumbnail(first_frame, target_thumb)
        info_video["thumbnail_path"] = str(target_thumb)

    return hash_results, info_video


# Backward compatibility aliases
hitung_phash = calculate_phash
hitung_dhash = calculate_dhash
jarak_hamming = hamming_distance
proses_video_ke_hash = process_video_hashes
