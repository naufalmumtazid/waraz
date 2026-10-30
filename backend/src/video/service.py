"""Business logic service layer for Feature 2: Recycled Video Tracker.

Manages video archive registration, detection pipelines, database transactions,
and privacy-compliant temporary file management.
"""

import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ..db.models import FrameHash, VideoArchive, VideoResult
from .config import FRAME_INTERVAL_SECONDS, TEMP_DIR, THUMBNAIL_DIR
from .extraction import save_thumbnail
from .hashing import process_video_hashes
from .matching import search_archive

logger = logging.getLogger("waraz.video.service")


def register_video_archive(
    db: Session,
    video_path: str | Path,
    judul: str,
    tanggal_asli: Optional[str] = None,
    sumber: Optional[str] = None,
    tautan: Optional[str] = None,
) -> Dict[str, Any]:
    """Registers a new verified video clip into the archive database.

    Enforces zero-retention policy: raw video files are discarded after keyframe
    extraction; only perceptual hash strings and 1 representative thumbnail are stored.
    """
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    title_clean = judul.strip()
    if not title_clean:
        raise ValueError("Video archive title cannot be empty.")

    # Check duplicate title
    duplicate = db.query(VideoArchive).filter(VideoArchive.judul.ilike(title_clean)).first()
    if duplicate:
        raise ValueError(f"Video with title '{title_clean}' already exists in archive (ID: {duplicate.id}).")

    frames_data, info_video = process_video_hashes(
        path,
        interval_seconds=FRAME_INTERVAL_SECONDS,
    )

    if not frames_data:
        raise ValueError("Failed to extract keyframes from the provided video.")

    # 1. Insert VideoArchive record
    archive_id = str(uuid.uuid4())
    archive = VideoArchive(
        id=archive_id,
        judul=title_clean,
        tanggal_asli=tanggal_asli,
        sumber=sumber,
        tautan=tautan,
    )
    db.add(archive)

    # 2. Insert FrameHash records
    for item in frames_data:
        fh = FrameHash(
            id=str(uuid.uuid4()),
            arsip_video_id=archive_id,
            urutan=item["urutan"],
            hash=item["phash"],
            dhash=item["dhash"],
        )
        db.add(fh)

    # 3. Save representative thumbnail (frame 0)
    thumb_path = THUMBNAIL_DIR / f"{archive_id}.jpg"
    save_thumbnail(frames_data[0]["image"], thumb_path)

    db.commit()
    db.refresh(archive)

    return {
        "id": archive.id,
        "judul": archive.judul,
        "tanggal_asli": archive.tanggal_asli,
        "sumber": archive.sumber,
        "tautan": archive.tautan,
        "total_frame_hash": len(frames_data),
        "durasi_detik": info_video["durasi_detik"],
        "thumbnail_path": str(thumb_path),
        "thumbnail_filename": f"{archive_id}.jpg",
    }


def detect_recycled_video(
    db: Session,
    video_path: str | Path,
    kasus_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Analyzes an input video to detect whether it is recycled footage from the archive."""
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    frames_data, info_video = process_video_hashes(
        path,
        interval_seconds=FRAME_INTERVAL_SECONDS,
    )

    if not frames_data:
        return {
            "status": "tidak_dapat_diproses",
            "skor": 0.0,
            "keyakinan": "rendah",
            "catatan": "Video tidak memiliki frame yang dapat diekstrak atau format tidak terbaca.",
            "info_video": info_video,
        }

    # Save query thumbnail for side-by-side comparison
    query_id = str(uuid.uuid4())
    query_thumb_filename = f"query_{query_id}.jpg"
    query_thumb_path = TEMP_DIR / query_thumb_filename
    save_thumbnail(frames_data[0]["image"], query_thumb_path)

    query_hashes = [f["phash"] for f in frames_data]
    query_dhashes = [f["dhash"] for f in frames_data]

    # Perform sequential matching
    match_result = search_archive(
        db=db,
        query_hashes=query_hashes,
        query_dhashes=query_dhashes,
    )

    if match_result.get("arsip_tercocok"):
        arch_id = match_result["arsip_tercocok"]["id"]
        match_result["arsip_tercocok"]["thumbnail_filename"] = f"{arch_id}.jpg"

    # Save to VideoResult table if case_id is supplied
    result_id = None
    if kasus_id:
        arch_id_fk = (
            match_result["arsip_tercocok"]["id"]
            if match_result.get("arsip_tercocok")
            else None
        )
        vr = VideoResult(
            id=str(uuid.uuid4()),
            kasus_id=kasus_id,
            arsip_video_id=arch_id_fk,
            skor=match_result["skor"],
            frame_cocok=match_result["frame_cocok"],
            frame_total=match_result["frame_total"],
            keyakinan=match_result["keyakinan"],
        )
        db.add(vr)
        db.commit()
        db.refresh(vr)
        result_id = vr.id

    return {
        **match_result,
        "hasil_video_id": result_id,
        "query_thumbnail_filename": query_thumb_filename,
        "info_video": info_video,
    }


def get_archive_list(db: Session) -> List[Dict[str, Any]]:
    """Retrieves all archived video records with frame counts and thumbnail status."""
    all_archives = db.query(VideoArchive).all()
    results = []
    for item in all_archives:
        total_frame = db.query(FrameHash).filter(FrameHash.arsip_video_id == item.id).count()
        thumb_filename = f"{item.id}.jpg"
        thumb_exists = (THUMBNAIL_DIR / thumb_filename).exists()

        results.append({
            "id": item.id,
            "judul": item.judul,
            "tanggal_asli": item.tanggal_asli,
            "sumber": item.sumber,
            "tautan": item.tautan,
            "total_frame": total_frame,
            "thumbnail_filename": thumb_filename if thumb_exists else None,
        })
    return results


def delete_archive_video(db: Session, archive_id: str) -> bool:
    """Deletes an archive record and its associated thumbnail."""
    archive = db.query(VideoArchive).filter(VideoArchive.id == archive_id).first()
    if not archive:
        return False

    thumb_path = THUMBNAIL_DIR / f"{archive_id}.jpg"
    if thumb_path.exists():
        try:
            thumb_path.unlink()
        except Exception:
            pass

    db.delete(archive)
    db.commit()
    return True


# Backward compatibility aliases
daftarkan_video_arsip = register_video_archive
deteksi_video_daur_ulang = detect_recycled_video
dapatkan_daftar_arsip = get_archive_list
hapus_video_arsip = delete_archive_video
