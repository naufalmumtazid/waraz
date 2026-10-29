"""Modul hashing perceptual untuk Fitur 2: Pelacak Video Daur Ulang.

Menggunakan imagehash (pHash dan dHash) untuk menghasilkan representasi
visual kompak yang tangguh terhadap kompresi, cropping kecil, dan perubahan resolusi.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import imagehash
from PIL import Image

from .ekstraksi import dapatkan_info_video, ekstrak_frame, simpan_thumbnail
from .konfigurasi import HASH_SIZE, INTERVAL_DETIK, THUMBNAIL_DIR

logger = logging.getLogger(__name__)


def hitung_phash(image: Image.Image, hash_size: int = HASH_SIZE) -> str:
    """Menghitung perceptual hash (pHash - DCT based) dari sebuah gambar.

    Args:
        image: Objek PIL Image.
        hash_size: Ukuran dimensi hash (default 8 -> 64-bit).

    Returns:
        String representasi hex (16 karakter untuk 64-bit).
    """
    ph = imagehash.phash(image, hash_size=hash_size)
    return str(ph)


def hitung_dhash(image: Image.Image, hash_size: int = HASH_SIZE) -> str:
    """Menghitung difference hash (dHash - gradient based) dari sebuah gambar.

    Args:
        image: Objek PIL Image.
        hash_size: Ukuran dimensi hash (default 8).

    Returns:
        String representasi hex.
    """
    dh = imagehash.dhash(image, hash_size=hash_size)
    return str(dh)


def jarak_hamming(hash1: str, hash2: str) -> int:
    """Menghitung jarak Hamming antara dua string hexadecimal hash.

    Jarak 0 menunjukkan dua gambar identik secara perseptual.
    Jarak <= 10 biasanya menunjukkan modifikasi ringan/daur ulang.

    Args:
        hash1: Hex string hash pertama.
        hash2: Hex string hash kedua.

    Returns:
        Jumlah bit yang berbeda (0 sampai 64 untuk hash 64-bit).
    """
    try:
        val1 = int(hash1, 16)
        val2 = int(hash2, 16)
        return bin(val1 ^ val2).count("1")
    except (ValueError, TypeError):
        # Fallback jika string bukan format hex yang valid
        return 64


def proses_video_ke_hash(
    video_path: str | Path,
    interval_detik: float = INTERVAL_DETIK,
    simpan_thumbnail_pertama: bool = False,
    thumbnail_path: Optional[str | Path] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Mengekstrak frame dari video dan menghitung hash untuk setiap frame.

    Args:
        video_path: Path berkas video yang akan diproses.
        interval_detik: Interval waktu antar keyframe.
        simpan_thumbnail_pertama: Jika True, simpan thumbnail frame pertama.
        thumbnail_path: Path tujuan jika ingin menyimpan thumbnail.

    Returns:
        Tuple:
            - List of dict: [
                {
                    "urutan": int,
                    "detik": float,
                    "phash": str,
                    "dhash": str,
                    "image": PIL.Image
                }, ...
              ]
            - Dict info video (fps, durasi, total_frame, resolusi)
    """
    path = Path(video_path)
    info_video = dapatkan_info_video(path)
    frames = ekstrak_frame(path, interval_detik=interval_detik)

    hasil_hash: List[Dict[str, Any]] = []

    for item in frames:
        pil_img = item["image"]
        ph = hitung_phash(pil_img)
        dh = hitung_dhash(pil_img)

        hasil_hash.append({
            "urutan": item["urutan"],
            "detik": item["detik"],
            "phash": ph,
            "dhash": dh,
            "image": pil_img,
        })

    # Simpan thumbnail pertama jika diminta
    if simpan_thumbnail_pertama and hasil_hash:
        pertama = hasil_hash[0]["image"]
        target_thumb = thumbnail_path or (THUMBNAIL_DIR / f"{path.stem}_thumb.jpg")
        simpan_thumbnail(pertama, target_thumb)
        info_video["thumbnail_path"] = str(target_thumb)

    return hasil_hash, info_video
