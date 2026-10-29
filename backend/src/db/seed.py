"""Seeder database WARAZ untuk inisialisasi data demo dan pengujian.

Membaca metadata dari `backend/data/contoh/arsip_video.csv`, menyiapkan klip video sintetis,
dan mendaftarkan rekaman arsip serta entitas pendukung (pengguna, kasus awal).

Dapat dijalankan langsung:
    python -m src.db.seed
"""

import csv
import logging
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy.orm import Session

try:
    from .koneksi import SessionLocal, init_db
    from .skema import ArsipVideo, Kasus, Pengguna
except ImportError:
    from src.db.koneksi import SessionLocal, init_db
    from src.db.skema import ArsipVideo, Kasus, Pengguna

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
CSV_PATH = DATA_DIR / "contoh" / "arsip_video.csv"
DEMO_VIDEOS_DIR = DATA_DIR / "demo_videos"


def seed_pengguna_dan_kasus(db: Session) -> Dict[str, Any]:
    """Menyiapkan pengguna default (analis) dan kasus contoh."""
    # Cek apakah pengguna sudah ada
    analis = db.query(Pengguna).filter(Pengguna.nama == "Analis Siber WARAZ").first()
    if not analis:
        analis = Pengguna(
            id="usr-analis-demo-01",
            nama="Analis Siber WARAZ",
            peran="analis",
        )
        db.add(analis)
        db.commit()
        db.refresh(analis)
        logger.info("Pengguna default dibuat: %s (%s)", analis.nama, analis.id)

    # Cek kasus default
    kasus = db.query(Kasus).filter(Kasus.judul.like("%Simulasi Gempa%")).first()
    if not kasus:
        kasus = Kasus(
            id="kasus-demo-video-01",
            pengguna_id=analis.id,
            judul="Investigasi Penyebaran Klip Video Bencana Gempa Lama",
            ringkasan="Pemeriksaan narasi disinformasi yang menggunakan kembali rekaman latihan lama seolah terjadi bencana baru.",
            tingkat_risiko="sedang",
            keyakinan="tinggi",
            status="baru",
        )
        db.add(kasus)
        db.commit()
        db.refresh(kasus)
        logger.info("Kasus contoh dibuat: %s (%s)", kasus.judul, kasus.id)

    return {"pengguna_id": analis.id, "kasus_id": kasus.id}


def seed_arsip_dari_csv(db: Session) -> List[Dict[str, Any]]:
    """Membaca `arsip_video.csv` dan mendaftarkan ke basis data arsip video."""
    try:
        from ..video.layanan import daftarkan_video_arsip
        from ..video.skrip_demo import siapkan_koleksi_demo
    except ImportError:
        from src.video.layanan import daftarkan_video_arsip
        from src.video.skrip_demo import siapkan_koleksi_demo

    # Pastikan video fisik demo telah dibuat
    video_map = siapkan_koleksi_demo()

    if not CSV_PATH.exists():
        logger.warning("Berkas CSV arsip tidak ditemukan di: %s", CSV_PATH)
        return []

    hasil_arsip: List[Dict[str, Any]] = []

    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            judul = row.get("judul", "").strip()
            berkas_video = row.get("berkas_video", "").strip()
            tanggal_asli = row.get("tanggal_asli", "").strip()
            sumber = row.get("sumber", "").strip()
            tautan = row.get("tautan", "").strip()

            # Cek apakah judul sudah ada di database
            existing = db.query(ArsipVideo).filter(ArsipVideo.judul == judul).first()
            if existing:
                logger.info("Arsip '%s' sudah terdaftar, melewati.", judul)
                continue

            # Cari video file di demo_videos
            v_path = DEMO_VIDEOS_DIR / berkas_video
            if not v_path.exists():
                # Cari fallback di video_map
                for key, mapped_path in video_map.items():
                    if mapped_path.name == berkas_video:
                        v_path = mapped_path
                        break

            if v_path.exists():
                info = daftarkan_video_arsip(
                    db=db,
                    video_path=v_path,
                    judul=judul,
                    tanggal_asli=tanggal_asli,
                    sumber=sumber,
                    tautan=tautan,
                )
                hasil_arsip.append(info)
                logger.info("Berhasil mendaftarkan arsip: %s (%d frames)", judul, info["total_frame_hash"])
            else:
                logger.warning("Berkas video untuk '%s' tidak ditemukan: %s", judul, berkas_video)

    return hasil_arsip


def jalankan_seeding():
    """Fungsi utama untuk menjalankan seluruh proses seeding."""
    init_db()
    db = SessionLocal()
    try:
        print("[*] Menjalankan seeding database WARAZ...")
        info_kasus = seed_pengguna_dan_kasus(db)
        print(f"[+] Pengguna dan kasus siap: {info_kasus}")

        arsip_baru = seed_arsip_dari_csv(db)
        print(f"[+] Selesai! {len(arsip_baru)} arsip baru berhasil didaftarkan.")
    finally:
        db.close()


if __name__ == "__main__":
    jalankan_seeding()
