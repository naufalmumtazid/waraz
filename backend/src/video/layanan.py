"""Modul layanan (business logic) untuk Fitur 2: Pelacak Video Daur Ulang.

Mengatur alur proses pendaftaran arsip, deteksi video daur ulang,
penyimpanan hasil ke database, serta integrasi dengan tabel HasilVideo.
"""

import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ..db.skema import ArsipVideo, HashFrame, HasilVideo
from .ekstraksi import simpan_thumbnail
from .hashing import proses_video_ke_hash
from .konfigurasi import (
    INTERVAL_DETIK,
    TEMP_DIR,
    THUMBNAIL_DIR,
)
from .pencocokan import cari_di_arsip

logger = logging.getLogger(__name__)


def daftarkan_video_arsip(
    db: Session,
    video_path: str | Path,
    judul: str,
    tanggal_asli: Optional[str] = None,
    sumber: Optional[str] = None,
    tautan: Optional[str] = None,
) -> Dict[str, Any]:
    """Mendaftarkan klip video baru ke dalam arsip database WARAZ.

    Catatan: Sesuai prinsip etika WARAZ, berkas video fisik TIDAK disimpan permanen.
    Yang disimpan di database hanya metadata (judul, sumber, dll) dan perceptual hash
    per frame-nya. Satu gambar thumbnail representatif disimpan untuk perbandingan visual.

    Args:
        db: Session SQLAlchemy.
        video_path: Path berkas video.
        judul: Judul atau deskripsi peristiwa dalam klip.
        tanggal_asli: Tanggal asli rekaman (misal YYYY-MM-DD).
        sumber: Sumber awal penyebaran (misal nama instansi atau kanal berita).
        tautan: Tautan referensi resmi/orisinal.

    Returns:
        Dict info rekaman arsip yang berhasil dibuat.
    """
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Berkas video tidak ditemukan di: {video_path}")

    frames_data, info_video = proses_video_ke_hash(
        path,
        interval_detik=INTERVAL_DETIK,
    )

    if not frames_data:
        raise ValueError("Gagal mengekstrak frame dari video yang diberikan.")

    # 1. Buat record ArsipVideo
    arsip_id = str(uuid.uuid4())
    arsip = ArsipVideo(
        id=arsip_id,
        judul=judul,
        tanggal_asli=tanggal_asli,
        sumber=sumber,
        tautan=tautan,
    )
    db.add(arsip)

    # 2. Simpan frame pHash
    for item in frames_data:
        hf = HashFrame(
            id=str(uuid.uuid4()),
            arsip_video_id=arsip_id,
            urutan=item["urutan"],
            hash=item["phash"],
            dhash=item["dhash"],
        )
        db.add(hf)

    # 3. Simpan satu thumbnail representatif (frame 0)
    thumb_path = THUMBNAIL_DIR / f"{arsip_id}.jpg"
    simpan_thumbnail(frames_data[0]["image"], thumb_path)

    db.commit()
    db.refresh(arsip)

    return {
        "id": arsip.id,
        "judul": arsip.judul,
        "tanggal_asli": arsip.tanggal_asli,
        "sumber": arsip.sumber,
        "tautan": arsip.tautan,
        "total_frame_hash": len(frames_data),
        "durasi_detik": info_video["durasi_detik"],
        "thumbnail_path": str(thumb_path),
        "thumbnail_filename": f"{arsip_id}.jpg",
    }


def deteksi_video_daur_ulang(
    db: Session,
    video_path: str | Path,
    kasus_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Menganalisis video input untuk mendeteksi apakah merupakan daur ulang dari arsip.

    Alur:
    1. Ekstrak frame dan hitung pHash dari video input.
    2. Simpan thumbnail pertama dari video input untuk preview perbandingan.
    3. Cocokkan sequence hash dengan seluruh video yang ada di arsip.
    4. Jika kasus_id disertakan, simpan hasil analisis ke tabel HasilVideo.
    5. Kembalikan data lengkap untuk tampilan UI berdampingan.

    Args:
        db: Session SQLAlchemy.
        video_path: Path berkas video yang diunggah/diperiksa.
        kasus_id: ID kasus opsional jika dipanggil dalam konteks penyelidikan kasus.

    Returns:
        Dict hasil analisis lengkap.
    """
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Berkas video tidak ditemukan di: {video_path}")

    frames_data, info_video = proses_video_ke_hash(
        path,
        interval_detik=INTERVAL_DETIK,
    )

    if not frames_data:
        return {
            "status": "tidak_dapat_diproses",
            "skor": 0.0,
            "keyakinan": "rendah",
            "catatan": "Video tidak memiliki frame yang dapat diekstrak atau format tidak terbaca.",
            "info_video": info_video,
        }

    # Simpan thumbnail video query ke direktori sementara
    query_id = str(uuid.uuid4())
    query_thumb_filename = f"query_{query_id}.jpg"
    query_thumb_path = TEMP_DIR / query_thumb_filename
    simpan_thumbnail(frames_data[0]["image"], query_thumb_path)

    # Ekstrak daftar pHash dan dHash
    query_hashes = [f["phash"] for f in frames_data]
    query_dhashes = [f["dhash"] for f in frames_data]

    # Jalankan pencocokan sequence
    hasil_pencocokan = cari_di_arsip(
        db=db,
        query_hashes=query_hashes,
        query_dhashes=query_dhashes,
    )

    # Tentukan thumbnail arsip jika ditemukan
    arsip_thumb_filename = None
    if hasil_pencocokan.get("arsip_tercocok"):
        arsip_id = hasil_pencocokan["arsip_tercocok"]["id"]
        arsip_thumb_filename = f"{arsip_id}.jpg"
        hasil_pencocokan["arsip_tercocok"]["thumbnail_filename"] = arsip_thumb_filename

    # Simpan ke tabel HasilVideo jika kasus_id tersedia
    hasil_video_id = None
    if kasus_id:
        arsip_id_fk = (
            hasil_pencocokan["arsip_tercocok"]["id"]
            if hasil_pencocokan.get("arsip_tercocok")
            else None
        )
        hv = HasilVideo(
            id=str(uuid.uuid4()),
            kasus_id=kasus_id,
            arsip_video_id=arsip_id_fk,
            skor=hasil_pencocokan["skor"],
            frame_cocok=hasil_pencocokan["frame_cocok"],
            frame_total=hasil_pencocokan["frame_total"],
            keyakinan=hasil_pencocokan["keyakinan"],
        )
        db.add(hv)
        db.commit()
        db.refresh(hv)
        hasil_video_id = hv.id

    hasil_akhir = {
        **hasil_pencocokan,
        "hasil_video_id": hasil_video_id,
        "query_thumbnail_filename": query_thumb_filename,
        "info_video": info_video,
    }

    return hasil_akhir


def dapatkan_daftar_arsip(db: Session) -> List[Dict[str, Any]]:
    """Mengambil semua daftar video yang ada di arsip.

    Args:
        db: Session SQLAlchemy.

    Returns:
        List of dict ringkasan arsip video.
    """
    semua = db.query(ArsipVideo).all()
    hasil = []
    for item in semua:
        total_frame = db.query(HashFrame).filter(HashFrame.arsip_video_id == item.id).count()
        thumb_filename = f"{item.id}.jpg"
        thumb_exists = (THUMBNAIL_DIR / thumb_filename).exists()

        hasil.append({
            "id": item.id,
            "judul": item.judul,
            "tanggal_asli": item.tanggal_asli,
            "sumber": item.sumber,
            "tautan": item.tautan,
            "total_frame": total_frame,
            "thumbnail_filename": thumb_filename if thumb_exists else None,
        })
    return hasil


def hapus_video_arsip(db: Session, arsip_id: str) -> bool:
    """Menghapus rekaman arsip video berdasarkan ID.

    Args:
        db: Session SQLAlchemy.
        arsip_id: ID arsip yang akan dihapus.

    Returns:
        True jika berhasil dihapus, False jika tidak ditemukan.
    """
    arsip = db.query(ArsipVideo).filter(ArsipVideo.id == arsip_id).first()
    if not arsip:
        return False

    # Hapus file thumbnail jika ada
    thumb_path = THUMBNAIL_DIR / f"{arsip_id}.jpg"
    if thumb_path.exists():
        thumb_path.unlink()

    db.delete(arsip)
    db.commit()
    return True
