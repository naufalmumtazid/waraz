"""Fungsi utama pemeriksaan video untuk Fitur 2: Pelacak Video Daur Ulang.

Menyediakan fungsi terpadu `periksa_video()` yang menghubungkan
ekstraksi keyframe, perceptual hashing, pencocokan sekuensial,
dan penyimpanan hasil analisis ke database.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

try:
    from ..db.koneksi import SessionLocal
    from .layanan import deteksi_video_daur_ulang
except ImportError:
    from src.db.koneksi import SessionLocal
    from src.video.layanan import deteksi_video_daur_ulang

logger = logging.getLogger(__name__)


def periksa_video(
    video_path: str | Path,
    db: Optional[Session] = None,
    kasus_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Fungsi utama untuk memeriksa apakah suatu video terindikasi video daur ulang.

    Alur:
    1. Membaca video dan mengekstrak keyframe (interval 2 detik).
    2. Menghitung perceptual hash (pHash 64-bit dan dHash).
    3. Mencocokkan deretan hash dengan basis arsip (diagonal sliding window).
    4. Memastikan kecocokan berurutan (consecutive match >= 3) untuk mencegah false-positive.
    5. Menghasilkan skor kemiripan, tingkat keyakinan, dan perbandingan thumbnail.
    6. Menyimpan rekaman hasil ke tabel hasil_video jika kasus_id diberikan.

    Args:
        video_path: Path berkas video yang akan diperiksa.
        db: Sesi database SQLAlchemy (opsional; jika None, dibuat otomatis).
        kasus_id: ID kasus investigasi opsional untuk relasi database.

    Returns:
        Dict hasil pemeriksaan lengkap:
            - status: 'kemungkinan_daur_ulang' | 'tidak_ditemukan_di_arsip' | 'tidak_dapat_diproses'
            - skor: float kemiripan (0.0 - 1.0)
            - keyakinan: 'tinggi' | 'sedang' | 'rendah'
            - arsip_tercocok: dict metadata video sumber asli jika ditemukan
            - frame_cocok: jumlah frame yang cocok
            - frame_total: total frame query
            - consecutive_run: panjang rangkaian frame berurutan terpanjang
            - query_thumbnail_filename: nama file thumbnail video query
            - catatan: penjelasan ringkas untuk analis
            - info_video: durasi, fps, resolusi
    """
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Berkas video tidak ditemukan: {video_path}")

    # Jika session tidak diberikan, kelola session sendiri
    if db is None:
        local_db = SessionLocal()
        try:
            return deteksi_video_daur_ulang(
                db=local_db,
                video_path=path,
                kasus_id=kasus_id,
            )
        finally:
            local_db.close()
    else:
        return deteksi_video_daur_ulang(
            db=db,
            video_path=path,
            kasus_id=kasus_id,
        )


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1:
        target_path = sys.argv[1]
        print(f"[*] Memeriksa video: {target_path}")
        hasil = periksa_video(target_path)
        # Hapus field non-serializable jika ada
        hasil_cetak = {k: v for k, v in hasil.items() if k != "detail_pasangan"}
        print(json.dumps(hasil_cetak, indent=2))
    else:
        print("Penggunaan: python -m src.video.periksa <path_ke_video.mp4>")
