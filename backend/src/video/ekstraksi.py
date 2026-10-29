"""Modul ekstraksi frame video untuk Fitur 2: Pelacak Video Daur Ulang.

Menggunakan OpenCV (cv2) untuk membaca video dan mengambil frame
pada interval waktu tertentu (default: 2 detik).
Frame dikonversi ke format RGB dan PIL Image untuk diproses oleh hashing.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from .konfigurasi import INTERVAL_DETIK, THUMBNAIL_DIR

logger = logging.getLogger(__name__)


class VideoExtractionError(Exception):
    """Exception khusus jika terjadi kesalahan saat mengekstrak video."""
    pass


def dapatkan_info_video(video_path: str | Path) -> Dict[str, Any]:
    """Mendapatkan metadata dasar video (durasi, fps, total frame, resolusi).

    Args:
        video_path: Path ke berkas video.

    Returns:
        Dict berisi durasi (detik), fps, total_frame, lebar, tinggi.
    """
    path_str = str(video_path)
    cap = cv2.VideoCapture(path_str)
    if not cap.isOpened():
        raise VideoExtractionError(f"Gagal membuka berkas video: {path_str}")

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


def ekstrak_frame(
    video_path: str | Path,
    interval_detik: float = INTERVAL_DETIK,
) -> List[Dict[str, Any]]:
    """Mengekstrak keyframe dari video dengan interval detik tertentu.

    Args:
        video_path: Path ke berkas video.
        interval_detik: Interval waktu antar frame (default dari konfigurasi: 2.0s).

    Returns:
        List of dict berisi:
            - urutan: index frame ke-n (0-based)
            - detik: waktu frame dalam detik
            - image: objek PIL.Image (RGB)
    """
    path_str = str(video_path)
    cap = cv2.VideoCapture(path_str)
    if not cap.isOpened():
        raise VideoExtractionError(f"Gagal membuka berkas video: {path_str}")

    hasil_frame: List[Dict[str, Any]] = []

    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        durasi = total_frame / fps if fps > 0 else 0.0

        if durasi <= 0 or total_frame <= 0:
            # Coba baca setidaknya satu frame jika metadata frame_count tidak valid
            success, frame_bgr = cap.read()
            if success and frame_bgr is not None:
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb)
                hasil_frame.append({
                    "urutan": 0,
                    "detik": 0.0,
                    "image": pil_img,
                })
            return hasil_frame

        # Hitung waktu target untuk ekstraksi
        target_detik = 0.0
        urutan = 0

        while target_detik <= durasi:
            target_msec = target_detik * 1000.0
            cap.set(cv2.CAP_PROP_POS_MSEC, target_msec)
            success, frame_bgr = cap.read()

            if not success or frame_bgr is None:
                # Jika pembacaan msec gagal di ujung video, coba baca frame berikutnya
                break

            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)

            hasil_frame.append({
                "urutan": urutan,
                "detik": round(target_detik, 2),
                "image": pil_img,
            })

            urutan += 1
            target_detik += interval_detik

        # Jika video sangat pendek (< interval), pastikan setidaknya 1 frame tersimpan
        if not hasil_frame:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame_bgr = cap.read()
            if success and frame_bgr is not None:
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb)
                hasil_frame.append({
                    "urutan": 0,
                    "detik": 0.0,
                    "image": pil_img,
                })

        return hasil_frame

    finally:
        cap.release()


def simpan_thumbnail(
    image: Image.Image,
    output_path: str | Path,
    max_size: Tuple[int, int] = (320, 240),
) -> Path:
    """Menyimpan thumbnail gambar yang telah di-resize.

    Args:
        image: Objek PIL.Image.
        output_path: Lokasi tujuan penyimpanan.
        max_size: Ukuran maksimal thumbnail (lebar, tinggi).

    Returns:
        Path berkas thumbnail yang tersimpan.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    img_copy = image.copy()
    img_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
    img_copy.save(path, format="JPEG", quality=85)
    return path
