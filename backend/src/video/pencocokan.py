"""Modul pencocokan perceptual hash untuk Fitur 2: Pelacak Video Daur Ulang.

Mencocokkan urutan hash query dengan arsip di database menggunakan jarak Hamming.
Mendukung kombinasi dual-hash (pHash + dHash) untuk ketahanan ekstra terhadap
overlay banner, running text, dan kompresi.
Kecocokan dinyatakan VALID hanya jika terdapat rangkaian frame BERURUTAN
yang cocok (consecutive frame matching), mencegah false-positive dari frame statis.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from ..db.skema import ArsipVideo, HashFrame
from .hashing import jarak_hamming
from .konfigurasi import (
    AMBANG_HAMMING,
    AMBANG_KEYAKINAN_SEDANG,
    AMBANG_KEYAKINAN_TINGGI,
    MIN_BERURUTAN,
    STATUS_DAUR_ULANG,
    STATUS_TIDAK_DITEMUKAN,
)

logger = logging.getLogger(__name__)


def cocokkan_dua_sequence(
    query_hashes: List[str],
    arsip_hashes: List[str],
    query_dhashes: Optional[List[str]] = None,
    arsip_dhashes: Optional[List[str]] = None,
    ambang_hamming: int = AMBANG_HAMMING,
    min_berurutan: int = MIN_BERURUTAN,
) -> Dict[str, Any]:
    """Mencocokkan urutan hash dari video query dengan urutan hash dari satu arsip.

    Menggunakan algoritma diagonal sliding window untuk mencari kecocokan
    urutan temporal (sekuensial).

    Args:
        query_hashes: List pHash hex dari video query.
        arsip_hashes: List pHash hex dari video arsip.
        query_dhashes: List dHash hex opsional dari video query.
        arsip_dhashes: List dHash hex opsional dari video arsip.
        ambang_hamming: Batas toleransi jarak bit (default 10).
        min_berurutan: Minimal frame berurutan yang harus cocok.

    Returns:
        Dict hasil pencocokan berisi:
            - cocok: bool
            - max_consecutive: int
            - total_cocok: int
            - avg_hamming: float
            - skor: float (0.0 - 1.0)
            - detail_pasangan: list of dict pasangan frame yang cocok
    """
    n_q = len(query_hashes)
    n_a = len(arsip_hashes)

    if n_q == 0 or n_a == 0:
        return {
            "cocok": False,
            "max_consecutive": 0,
            "total_cocok": 0,
            "avg_hamming": 64.0,
            "skor": 0.0,
            "detail_pasangan": [],
        }

    terbaik = {
        "cocok": False,
        "max_consecutive": 0,
        "total_cocok": 0,
        "avg_hamming": 64.0,
        "skor": 0.0,
        "detail_pasangan": [],
    }

    min_d = -(n_q - 1)
    max_d = n_a - 1

    for d in range(min_d, max_d + 1):
        pasangan_diagonal: List[Dict[str, Any]] = []
        consecutive_saat_ini = 0
        max_consecutive_diagonal = 0

        start_q = max(0, -d)
        end_q = min(n_q, n_a - d)

        for q_idx in range(start_q, end_q):
            a_idx = q_idx + d

            dist_p = jarak_hamming(query_hashes[q_idx], arsip_hashes[a_idx])
            dist_d = None
            if (
                query_dhashes
                and arsip_dhashes
                and q_idx < len(query_dhashes)
                and a_idx < len(arsip_dhashes)
                and query_dhashes[q_idx]
                and arsip_dhashes[a_idx]
            ):
                dist_d = jarak_hamming(query_dhashes[q_idx], arsip_dhashes[a_idx])

            # Efektif jarak: jika dHash tersedia, gunakan jarak minimum (robust terhadap teks banner)
            dist_efektif = min(dist_p, dist_d) if dist_d is not None else dist_p

            if dist_efektif <= ambang_hamming:
                consecutive_saat_ini += 1
                if consecutive_saat_ini > max_consecutive_diagonal:
                    max_consecutive_diagonal = consecutive_saat_ini

                pasangan_diagonal.append({
                    "query_idx": q_idx,
                    "arsip_idx": a_idx,
                    "jarak": dist_efektif,
                    "dist_phash": dist_p,
                    "dist_dhash": dist_d,
                })
            else:
                consecutive_saat_ini = 0

        total_cocok = len(pasangan_diagonal)
        if total_cocok > 0:
            avg_dist = sum(p["jarak"] for p in pasangan_diagonal) / total_cocok
            sim_visual = max(0.0, 1.0 - (avg_dist / 64.0))

            coverage_query = total_cocok / n_q
            run_ratio = min(1.0, max_consecutive_diagonal / n_q)

            skor_diagonal = round(sim_visual * (0.5 + 0.3 * coverage_query + 0.2 * run_ratio), 4)

            syarat_berurutan = (
                max_consecutive_diagonal >= min_berurutan
                or (n_q < min_berurutan and max_consecutive_diagonal == n_q)
            )

            if syarat_berurutan and skor_diagonal > terbaik["skor"]:
                terbaik = {
                    "cocok": True,
                    "max_consecutive": max_consecutive_diagonal,
                    "total_cocok": total_cocok,
                    "avg_hamming": round(avg_dist, 2),
                    "skor": skor_diagonal,
                    "detail_pasangan": pasangan_diagonal,
                }

    return terbaik


def cari_di_arsip(
    db: Session,
    query_hashes: List[str],
    query_dhashes: Optional[List[str]] = None,
    ambang_hamming: int = AMBANG_HAMMING,
    min_berurutan: int = MIN_BERURUTAN,
) -> Dict[str, Any]:
    """Mencari apakah video query cocok dengan video manapun di dalam database arsip.

    Args:
        db: Session SQLAlchemy.
        query_hashes: List string hex pHash dari video yang diuji.
        query_dhashes: List string hex dHash opsional.
        ambang_hamming: Ambang jarak Hamming maksimal per frame.
        min_berurutan: Minimal frame berurutan yang wajib cocok.

    Returns:
        Dict lengkap hasil evaluasi terhadap seluruh arsip.
    """
    frame_total = len(query_hashes)

    if frame_total == 0:
        return {
            "status": "tidak_dapat_diproses",
            "skor": 0.0,
            "keyakinan": "rendah",
            "frame_cocok": 0,
            "frame_total": 0,
            "consecutive_run": 0,
            "arsip_tercocok": None,
            "detail_pasangan": [],
            "catatan": "Video tidak menghasilkan frame yang dapat dianalisis.",
        }

    semua_arsip = db.query(ArsipVideo).all()

    if not semua_arsip:
        return {
            "status": STATUS_TIDAK_DITEMUKAN,
            "skor": 0.0,
            "keyakinan": "rendah",
            "frame_cocok": 0,
            "frame_total": frame_total,
            "consecutive_run": 0,
            "arsip_tercocok": None,
            "detail_pasangan": [],
            "catatan": "Arsip database masih kosong. Belum ada klip pembanding.",
        }

    kandidat_terbaik: Optional[Dict[str, Any]] = None
    arsip_pilihan: Optional[ArsipVideo] = None

    for arsip in semua_arsip:
        arsip_frames = (
            db.query(HashFrame)
            .filter(HashFrame.arsip_video_id == arsip.id)
            .order_by(HashFrame.urutan.asc())
            .all()
        )
        arsip_hashes = [f.hash for f in arsip_frames]
        arsip_dhashes = [f.dhash for f in arsip_frames]

        hasil_dua = cocokkan_dua_sequence(
            query_hashes=query_hashes,
            arsip_hashes=arsip_hashes,
            query_dhashes=query_dhashes,
            arsip_dhashes=arsip_dhashes,
            ambang_hamming=ambang_hamming,
            min_berurutan=min_berurutan,
        )

        if hasil_dua["cocok"]:
            if kandidat_terbaik is None or hasil_dua["skor"] > kandidat_terbaik["skor"]:
                kandidat_terbaik = hasil_dua
                arsip_pilihan = arsip

    if kandidat_terbaik and arsip_pilihan:
        skor = kandidat_terbaik["skor"]

        if skor >= AMBANG_KEYAKINAN_TINGGI and kandidat_terbaik["max_consecutive"] >= min_berurutan:
            keyakinan = "tinggi"
        elif skor >= AMBANG_KEYAKINAN_SEDANG:
            keyakinan = "sedang"
        else:
            keyakinan = "rendah"

        catatan = (
            f"Ditemukan {kandidat_terbaik['total_cocok']} frame cocok "
            f"({kandidat_terbaik['max_consecutive']} frame berurutan) "
            f"dengan arsip '{arsip_pilihan.judul}'."
        )

        return {
            "status": STATUS_DAUR_ULANG,
            "skor": skor,
            "keyakinan": keyakinan,
            "frame_cocok": kandidat_terbaik["total_cocok"],
            "frame_total": frame_total,
            "consecutive_run": kandidat_terbaik["max_consecutive"],
            "avg_hamming": kandidat_terbaik["avg_hamming"],
            "arsip_tercocok": {
                "id": arsip_pilihan.id,
                "judul": arsip_pilihan.judul,
                "tanggal_asli": arsip_pilihan.tanggal_asli,
                "sumber": arsip_pilihan.sumber,
                "tautan": arsip_pilihan.tautan,
            },
            "detail_pasangan": kandidat_terbaik["detail_pasangan"],
            "catatan": catatan,
        }

    return {
        "status": STATUS_TIDAK_DITEMUKAN,
        "skor": 0.0,
        "keyakinan": "rendah",
        "frame_cocok": 0,
        "frame_total": frame_total,
        "consecutive_run": 0,
        "arsip_tercocok": None,
        "detail_pasangan": [],
        "catatan": (
            "Tidak ditemukan kecocokan berurutan di dalam arsip klip yang tersimpan. "
            "Catatan: tidak ditemukan di arsip bukan berarti video pasti baru/orisinal."
        ),
    }
