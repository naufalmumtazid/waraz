"""Sequence matching algorithm for Feature 2: Recycled Video Tracker.

Matches query frame hash sequences against database archives using
diagonal sliding window temporal alignment and Hamming distance.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from ..db.models import FrameHash, VideoArchive
from .config import (
    CONFIDENCE_HIGH_THRESHOLD,
    CONFIDENCE_MEDIUM_THRESHOLD,
    HAMMING_THRESHOLD,
    MIN_CONSECUTIVE_FRAMES,
    STATUS_NOT_FOUND,
    STATUS_RECYCLED,
)
from .hashing import hamming_distance

logger = logging.getLogger("waraz.video.matching")


def match_two_sequences(
    query_hashes: List[str],
    archive_hashes: List[str],
    query_dhashes: Optional[List[str]] = None,
    archive_dhashes: Optional[List[str]] = None,
    hamming_threshold: int = HAMMING_THRESHOLD,
    min_consecutive: int = MIN_CONSECUTIVE_FRAMES,
) -> Dict[str, Any]:
    """Matches two frame sequences using diagonal sliding window alignment."""
    n_q = len(query_hashes)
    n_a = len(archive_hashes)

    if n_q == 0 or n_a == 0:
        return {
            "cocok": False,
            "max_consecutive": 0,
            "total_cocok": 0,
            "avg_hamming": 64.0,
            "skor": 0.0,
            "detail_pasangan": [],
        }

    best = {
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
        diagonal_pairs: List[Dict[str, Any]] = []
        current_consecutive = 0
        max_consecutive_diag = 0

        start_q = max(0, -d)
        end_q = min(n_q, n_a - d)

        for q_idx in range(start_q, end_q):
            a_idx = q_idx + d

            dist_p = hamming_distance(query_hashes[q_idx], archive_hashes[a_idx])
            dist_d = None
            if (
                query_dhashes
                and archive_dhashes
                and q_idx < len(query_dhashes)
                and a_idx < len(archive_dhashes)
                and query_dhashes[q_idx]
                and archive_dhashes[a_idx]
            ):
                dist_d = hamming_distance(query_dhashes[q_idx], archive_dhashes[a_idx])

            effective_dist = min(dist_p, dist_d) if dist_d is not None else dist_p

            if effective_dist <= hamming_threshold:
                current_consecutive += 1
                if current_consecutive > max_consecutive_diag:
                    max_consecutive_diag = current_consecutive

                diagonal_pairs.append({
                    "query_idx": q_idx,
                    "arsip_idx": a_idx,
                    "jarak": effective_dist,
                    "dist_phash": dist_p,
                    "dist_dhash": dist_d,
                })
            else:
                current_consecutive = 0

        total_matched = len(diagonal_pairs)
        if total_matched > 0:
            avg_dist = sum(p["jarak"] for p in diagonal_pairs) / total_matched
            sim_visual = max(0.0, 1.0 - (avg_dist / 64.0))

            coverage_query = total_matched / n_q
            run_ratio = min(1.0, max_consecutive_diag / n_q)

            diag_score = round(sim_visual * (0.5 + 0.3 * coverage_query + 0.2 * run_ratio), 4)

            consecutive_valid = (
                max_consecutive_diag >= min_consecutive
                or (n_q < min_consecutive and max_consecutive_diag == n_q)
            )

            if consecutive_valid and diag_score > best["skor"]:
                best = {
                    "cocok": True,
                    "max_consecutive": max_consecutive_diag,
                    "total_cocok": total_matched,
                    "avg_hamming": round(avg_dist, 2),
                    "skor": diag_score,
                    "detail_pasangan": diagonal_pairs,
                }

    return best


def search_archive(
    db: Session,
    query_hashes: List[str],
    query_dhashes: Optional[List[str]] = None,
    hamming_threshold: int = HAMMING_THRESHOLD,
    min_consecutive: int = MIN_CONSECUTIVE_FRAMES,
) -> Dict[str, Any]:
    """Searches entire database archive for matching consecutive sequence."""
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

    all_archives = db.query(VideoArchive).all()

    if not all_archives:
        return {
            "status": STATUS_NOT_FOUND,
            "skor": 0.0,
            "keyakinan": "rendah",
            "frame_cocok": 0,
            "frame_total": frame_total,
            "consecutive_run": 0,
            "arsip_tercocok": None,
            "detail_pasangan": [],
            "catatan": "Arsip database masih kosong. Belum ada klip pembanding.",
        }

    best_match: Optional[Dict[str, Any]] = None
    selected_archive: Optional[VideoArchive] = None

    for archive in all_archives:
        archive_frames = (
            db.query(FrameHash)
            .filter(FrameHash.arsip_video_id == archive.id)
            .order_by(FrameHash.urutan.asc())
            .all()
        )
        arch_hashes = [f.hash for f in archive_frames]
        arch_dhashes = [f.dhash for f in archive_frames]

        result = match_two_sequences(
            query_hashes=query_hashes,
            archive_hashes=arch_hashes,
            query_dhashes=query_dhashes,
            archive_dhashes=arch_dhashes,
            hamming_threshold=hamming_threshold,
            min_consecutive=min_consecutive,
        )

        if result["cocok"]:
            if best_match is None or result["skor"] > best_match["skor"]:
                best_match = result
                selected_archive = archive

    if best_match and selected_archive:
        skor = best_match["skor"]

        if skor >= CONFIDENCE_HIGH_THRESHOLD and best_match["max_consecutive"] >= min_consecutive:
            confidence = "tinggi"
        elif skor >= CONFIDENCE_MEDIUM_THRESHOLD:
            confidence = "sedang"
        else:
            confidence = "rendah"

        catatan = (
            f"Ditemukan {best_match['total_cocok']} frame cocok "
            f"({best_match['max_consecutive']} frame berurutan) "
            f"dengan arsip '{selected_archive.judul}'."
        )

        return {
            "status": STATUS_RECYCLED,
            "skor": skor,
            "keyakinan": confidence,
            "frame_cocok": best_match["total_cocok"],
            "frame_total": frame_total,
            "consecutive_run": best_match["max_consecutive"],
            "avg_hamming": best_match["avg_hamming"],
            "arsip_tercocok": {
                "id": selected_archive.id,
                "judul": selected_archive.judul,
                "tanggal_asli": selected_archive.tanggal_asli,
                "sumber": selected_archive.sumber,
                "tautan": selected_archive.tautan,
            },
            "detail_pasangan": best_match["detail_pasangan"],
            "catatan": catatan,
        }

    return {
        "status": STATUS_NOT_FOUND,
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


# Backward compatibility aliases
cocokkan_dua_sequence = match_two_sequences
cari_di_arsip = search_archive
