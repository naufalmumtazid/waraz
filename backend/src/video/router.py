"""FastAPI Router untuk Fitur 2: Pelacak Video Daur Ulang.

Menyediakan REST API untuk:
- Deteksi video daur ulang (upload & analisis instan)
- Manajemen arsip video (daftar, tambah, hapus)
- Seeding data demo fiktif
- Pengambilan gambar thumbnail untuk komparasi side-by-side
"""

import logging
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..db.koneksi import get_db
from .konfigurasi import TEMP_DIR, THUMBNAIL_DIR
from .layanan import (
    dapatkan_daftar_arsip,
    daftarkan_video_arsip,
    deteksi_video_daur_ulang,
    hapus_video_arsip,
)
from .skrip_demo import seed_arsip_demo, siapkan_koleksi_demo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/video", tags=["Pelacak Video Daur Ulang (F2)"])


@router.post("/deteksi", summary="Deteksi penggunaan video daur ulang")
async def api_deteksi_video(
    file: UploadFile = File(..., description="Berkas video yang ingin dianalisis (mp4, mkv, avi, webm)"),
    kasus_id: Optional[str] = Form(None, description="ID kasus jika terkait investigasi"),
    db: Session = Depends(get_db),
):
    """Mendeteksi apakah video yang diunggah merupakan daur ulang dari video lama di arsip.

    Proses:
    - Ekstraksi keyframe setiap 2 detik.
    - Perceptual hashing (pHash 64-bit).
    - Sequential distance matching dengan arsip.
    - Pembersihan otomatis berkas video asli setelah ekstraksi (etika privasi).
    """
    ext = Path(file.filename or "video.mp4").suffix or ".mp4"
    temp_filename = f"upload_{uuid.uuid4()}{ext}"
    temp_path = TEMP_DIR / temp_filename

    try:
        # Simpan sementara berkas unggahan
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Proses analisis
        hasil = deteksi_video_daur_ulang(
            db=db,
            video_path=temp_path,
            kasus_id=kasus_id,
        )

        return hasil

    except Exception as e:
        logger.exception("Kesalahan saat memproses deteksi video: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan saat memproses video: {str(e)}",
        )
    finally:
        # Prinsip Etika WARAZ: Hapus berkas video mentah setelah analisis selesai
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass


@router.post("/arsip", summary="Daftarkan video baru ke arsip")
async def api_tambah_arsip(
    file: UploadFile = File(..., description="Berkas video acuan arsip"),
    judul: str = Form(..., description="Judul atau konteks video asli"),
    tanggal_asli: Optional[str] = Form(None, description="Tanggal kejadian asli (YYYY-MM-DD)"),
    sumber: Optional[str] = Form(None, description="Sumber resmi atau penerbit awal"),
    tautan: Optional[str] = Form(None, description="Tautan publikasi orisinal"),
    db: Session = Depends(get_db),
):
    """Menambahkan video acuan baru ke dalam arsip perceptual hash."""
    ext = Path(file.filename or "video.mp4").suffix or ".mp4"
    temp_filename = f"arsip_raw_{uuid.uuid4()}{ext}"
    temp_path = TEMP_DIR / temp_filename

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        info_arsip = daftarkan_video_arsip(
            db=db,
            video_path=temp_path,
            judul=judul,
            tanggal_asli=tanggal_asli,
            sumber=sumber,
            tautan=tautan,
        )
        return info_arsip

    except Exception as e:
        logger.exception("Kesalahan saat mendaftarkan arsip video: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mendaftarkan arsip video: {str(e)}",
        )
    finally:
        # Simpan hanya hash & thumbnail, hapus video fisik mentah
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass


@router.get("/arsip", summary="Daftar semua arsip video")
def api_daftar_arsip(db: Session = Depends(get_db)):
    """Mengambil seluruh data arsip video yang terdaftar beserta status thumbnail."""
    return dapatkan_daftar_arsip(db)


@router.delete("/arsip/{arsip_id}", summary="Hapus video dari arsip")
def api_hapus_arsip(arsip_id: str, db: Session = Depends(get_db)):
    """Menghapus entitas arsip video dan hash frame terkait."""
    berhasil = hapus_video_arsip(db=db, arsip_id=arsip_id)
    if not berhasil:
        raise HTTPException(status_code=404, detail="Arsip video tidak ditemukan.")
    return {"status": "sukses", "pesan": f"Arsip video {arsip_id} berhasil dihapus."}


@router.post("/seed-demo", summary="Isi arsip demo otomatis")
def api_seed_demo(db: Session = Depends(get_db)):
    """Menghasilkan video sintetis dan mengisi arsip demo secara otomatis."""
    try:
        terdaftar = seed_arsip_demo(db=db)
        return {
            "status": "sukses",
            "jumlah_arsip_baru": len(terdaftar),
            "arsip_terdaftar": terdaftar,
            "pesan": "Basis arsip demo berhasil disiapkan.",
        }
    except Exception as e:
        logger.exception("Gagal seeding data demo: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Gagal membuat arsip demo: {str(e)}",
        )


@router.get("/thumbnail/{tipe}/{filename}", summary="Ambil gambar thumbnail")
def api_ambil_thumbnail(tipe: str, filename: str):
    """Menyajikan berkas gambar thumbnail untuk visualisasi side-by-side.

    - tipe: 'arsip' (dari direktori data/thumbnails) atau 'temp' (dari data/temp)
    """
    if tipe == "arsip":
        target = THUMBNAIL_DIR / filename
    elif tipe == "temp":
        target = TEMP_DIR / filename
    else:
        raise HTTPException(status_code=400, detail="Tipe thumbnail tidak valid.")

    if not target.exists():
        raise HTTPException(status_code=404, detail="Gambar thumbnail tidak ditemukan.")

    return FileResponse(path=str(target), media_type="image/jpeg")
