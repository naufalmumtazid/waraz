"""Generator video sintetis & seeder data demo untuk Fitur 2: Pelacak Video Daur Ulang.

Menghasilkan video demo fiktif secara lokal menggunakan OpenCV:
1. Video arsip asli (misal simulasi latihan/tanggap darurat)
2. Varian daur ulang:
   - Klip terpotong (cropped in time)
   - Klip dengan overlay teks provokatif
   - Klip resolusi terkompresi
3. Klip kontrol non-arsip (video baru yang tidak pernah ada di arsip)

Tujuan:
Memungkinkan pengujian presisi dan recall secara jujur, offline,
tanpa hak cipta, dan tanpa bergantung pada video eksternal.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
from sqlalchemy.orm import Session

from ..db.skema import ArsipVideo, HashFrame
from .konfigurasi import ARSIP_VIDEO_DIR, DATA_DIR, TEMP_DIR
from .layanan import daftarkan_video_arsip

logger = logging.getLogger(__name__)

DEMO_DIR = DATA_DIR / "demo_videos"
DEMO_DIR.mkdir(parents=True, exist_ok=True)


def buat_video_sintetis(
    output_path: Path,
    seed: int = 100,
    durasi_detik: int = 8,
    fps: int = 10,
    judul_teks: str = "SIMULASI LATIHAN BENCANA",
    overlay_tambahan: str = "",
    mulai_detik: float = 0.0,
    selesai_detik: float = 0.0,
) -> Path:
    """Membuat video sintetis dengan elemen visual kaya menggunakan OpenCV.

    Menggunakan procedural scene generator dengan seed tetap agar menghasilkan
    visual yang konsisten, kaya tekstur visual, dan realistis untuk pengujian pHash & dHash.
    """
    lebar, tinggi = 640, 360
    total_frame_asli = durasi_detik * fps

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(output_path), fourcc, float(fps), (lebar, tinggi))

    if not out.isOpened():
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(str(output_path), fourcc, float(fps), (lebar, tinggi))

    start_frame = int(mulai_detik * fps) if mulai_detik > 0 else 0
    end_frame = int(selesai_detik * fps) if selesai_detik > 0 else total_frame_asli

    # Tetapkan komponen visual dasar berbasis seed
    rng = np.random.RandomState(seed)
    sky_r = int(rng.randint(80, 220))
    sky_g = int(rng.randint(80, 200))
    sky_b = int(rng.randint(120, 255))
    ground_r = int(rng.randint(40, 90))
    ground_g = int(rng.randint(80, 140))
    ground_b = int(rng.randint(40, 90))

    # Objek-objek latar belakang (gedung / pohon / marka)
    benda_bg = []
    for _ in range(12):
        bx = int(rng.randint(10, lebar - 80))
        bw = int(rng.randint(35, 90))
        bh = int(rng.randint(60, 160))
        bc = (int(rng.randint(40, 180)), int(rng.randint(40, 180)), int(rng.randint(40, 180)))
        benda_bg.append((bx, bw, bh, bc))

    for f_idx in range(total_frame_asli):
        if f_idx < start_frame or f_idx >= end_frame:
            continue

        frame = np.zeros((tinggi, lebar, 3), dtype=np.uint8)

        # Langit dan tanah
        frame[:200, :] = (sky_b, sky_g, sky_r)
        frame[200:, :] = (ground_b, ground_g, ground_r)

        # Gambar benda-benda latar belakang
        for bx, bw, bh, bc in benda_bg:
            cv2.rectangle(frame, (bx, 200 - bh), (bx + bw, 200), bc, -1)
            # Detail jendela
            for wx in range(bx + 6, bx + bw - 6, 16):
                for wy in range(200 - bh + 12, 195, 22):
                    cv2.rectangle(frame, (wx, wy), (wx + 8, wy + 12), (220, 240, 255), -1)

        # Garis horizontal jalan
        cv2.line(frame, (0, 200), (lebar, 200), (30, 30, 30), 2)
        cv2.rectangle(frame, (0, 280), (lebar, tinggi), (50, 50, 50), -1)

        # Marka jalan bergerak
        offset_jalan = int((f_idx * 15) % 80)
        for mx in range(-80 + offset_jalan, lebar + 80, 80):
            cv2.rectangle(frame, (mx, 315), (mx + 40, 325), (255, 255, 255), -1)

        # Kendaraan / objek bergerak di depan
        pos_x = int(50 + (f_idx / total_frame_asli) * (lebar - 100))
        pos_y = 260
        cv2.rectangle(frame, (pos_x, pos_y - 30), (pos_x + 90, pos_y + 15), (0, 140, 255), -1)
        cv2.circle(frame, (pos_x + 20, pos_y + 18), 12, (20, 20, 20), -1)
        cv2.circle(frame, (pos_x + 70, pos_y + 18), 12, (20, 20, 20), -1)

        # Teks judul atas
        cv2.putText(
            frame,
            judul_teks,
            (30, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        # Timestamp simulasi
        detik_berjalan = f_idx / fps
        cv2.putText(
            frame,
            f"DURASI: 00:{int(detik_berjalan):02d}",
            (30, tinggi - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (220, 220, 220),
            1,
            cv2.LINE_AA,
        )

        # Overlay tambahan (simulasi daur ulang dengan banner berita bohong)
        if overlay_tambahan:
            cv2.rectangle(frame, (0, 75), (lebar, 125), (0, 0, 200), -1)
            cv2.putText(
                frame,
                overlay_tambahan,
                (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        out.write(frame)

    out.release()
    return output_path


def siapkan_koleksi_demo() -> Dict[str, Path]:
    """Membuat kumpulan video arsip dan variasi daur ulang untuk demonstrasi & evaluasi."""
    hasil: Dict[str, Path] = {}

    # 1. Arsip Asli 1: Simulasi Gempa
    p_arsip_1 = DEMO_DIR / "arsip_simulasi_gempa.mp4"
    buat_video_sintetis(
        p_arsip_1,
        seed=101,
        durasi_detik=8,
        fps=10,
        judul_teks="DOKUMENTASI SIMULASI GEMPA BPBD",
    )
    hasil["arsip_1"] = p_arsip_1

    # 2. Arsip Asli 2: Apel Siaga
    p_arsip_2 = DEMO_DIR / "arsip_apel_siaga.mp4"
    buat_video_sintetis(
        p_arsip_2,
        seed=202,
        durasi_detik=8,
        fps=10,
        judul_teks="APEL SIAGA PENGAMANAN KOTA",
    )
    hasil["arsip_2"] = p_arsip_2

    # 3. Arsip Asli 3: Konferensi Pers
    p_arsip_3 = DEMO_DIR / "arsip_konferensi_pers.mp4"
    buat_video_sintetis(
        p_arsip_3,
        seed=303,
        durasi_detik=8,
        fps=10,
        judul_teks="KONFERENSI PERS RESMI TAHUNAN",
    )
    hasil["arsip_3"] = p_arsip_3

    # 4. Varian Daur Ulang: Klip Terpotong (detik 2.0 sampai 6.0 dari arsip 1)
    p_uji_cut = DEMO_DIR / "uji_daur_ulang_potongan.mp4"
    buat_video_sintetis(
        p_uji_cut,
        seed=101,
        durasi_detik=8,
        fps=10,
        judul_teks="DOKUMENTASI SIMULASI GEMPA BPBD",
        mulai_detik=2.0,
        selesai_detik=6.0,
    )
    hasil["uji_cut"] = p_uji_cut

    # 5. Varian Daur Ulang: Beri Teks Provokatif (overlay banner pada arsip 2)
    p_uji_teks = DEMO_DIR / "uji_daur_ulang_banner_palsu.mp4"
    buat_video_sintetis(
        p_uji_teks,
        seed=202,
        durasi_detik=8,
        fps=10,
        judul_teks="APEL SIAGA PENGAMANAN KOTA",
        overlay_tambahan="DARURAT! KERUSUHAN PECAH DI PUSAT KOTA!",
    )
    hasil["uji_teks"] = p_uji_teks

    # 6. Kontrol Non-Arsip (Video sama sekali berbeda / bukan daur ulang)
    p_uji_baru = DEMO_DIR / "uji_video_orisinal_baru.mp4"
    buat_video_sintetis(
        p_uji_baru,
        seed=777,
        durasi_detik=8,
        fps=10,
        judul_teks="FESTIVAL SENI BUDAYA NUSANTARA",
    )
    hasil["uji_baru"] = p_uji_baru

    return hasil


def seed_arsip_demo(db: Session) -> List[Dict[str, Any]]:
    """Mengisi database arsip dengan video demo sintetis jika belum ada.

    Args:
        db: Session SQLAlchemy.

    Returns:
        List data arsip yang berhasil didaftarkan.
    """
    video_map = siapkan_koleksi_demo()
    terdaftar: List[Dict[str, Any]] = []

    count_arsip = db.query(ArsipVideo).count()
    if count_arsip > 0:
        logger.info("Database arsip sudah memiliki data (%d arsip).", count_arsip)
        return terdaftar

    a1 = daftarkan_video_arsip(
        db=db,
        video_path=video_map["arsip_1"],
        judul="Dokumentasi Simulasi Gempa Bumi dan Evakuasi Mandiri",
        tanggal_asli="2023-04-12",
        sumber="BPBD Jawa Barat / Humas Resmi",
        tautan="https://bpbd.jabarprov.go.id/simulasi-gempa-2023",
    )
    terdaftar.append(a1)

    a2 = daftarkan_video_arsip(
        db=db,
        video_path=video_map["arsip_2"],
        judul="Apel Gelar Pasukan Kesiapsiagaan Pengamanan Wilayah",
        tanggal_asli="2022-08-17",
        sumber="Penerangan Kodam / Dokumentasi Publik",
        tautan="https://tni.mil.id/berita/apel-kesiapsiagaan-2022",
    )
    terdaftar.append(a2)

    a3 = daftarkan_video_arsip(
        db=db,
        video_path=video_map["arsip_3"],
        judul="Konferensi Pers Tahunan Evaluasi Pelayanan Publik",
        tanggal_asli="2021-12-20",
        sumber="Biro Pers dan Media Sekretariat",
        tautan="https://kemendagri.go.id/siaran-pers/evaluasi-kinerja-2021",
    )
    terdaftar.append(a3)

    return terdaftar
