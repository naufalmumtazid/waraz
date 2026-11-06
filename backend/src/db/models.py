"""SQLAlchemy ORM models for WARAZ.

Supports both Supabase (PostgreSQL) and SQLite.
Includes models for Feature 2 (Recycled Video Tracker) and core system entities.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def _new_id() -> str:
    """Generates a new UUID4 as a string."""
    return str(uuid.uuid4())


def _now_iso() -> str:
    """Current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


class Base(DeclarativeBase):
    pass


# ─────────────────────────────────────────────────────────────
# Core Entities
# ─────────────────────────────────────────────────────────────


class User(Base):
    """System user or cyber analyst."""
    __tablename__ = "pengguna"

    id = Column(String, primary_key=True, default=_new_id)
    nama = Column(String, nullable=False)
    peran = Column(String, nullable=False)
    dibuat_pada = Column(String, nullable=False, default=_now_iso)

    __table_args__ = (
        CheckConstraint("peran IN ('pengguna','analis')", name="ck_pengguna_peran"),
    )


class Case(Base):
    """Investigation case containing analysis findings."""
    __tablename__ = "kasus"

    id = Column(String, primary_key=True, default=_new_id)
    pengguna_id = Column(String, ForeignKey("pengguna.id"), nullable=False)
    judul = Column(String, nullable=False)
    ringkasan = Column(Text, nullable=True)
    tingkat_risiko = Column(String, nullable=True)
    keyakinan = Column(String, nullable=True)
    status = Column(String, nullable=False, default="baru")
    dibuat_pada = Column(String, nullable=False, default=_now_iso)

    __table_args__ = (
        CheckConstraint(
            "tingkat_risiko IN ('rendah','sedang','tinggi')",
            name="ck_kasus_risiko",
        ),
        CheckConstraint(
            "keyakinan IN ('rendah','sedang','tinggi')",
            name="ck_kasus_keyakinan",
        ),
        CheckConstraint(
            "status IN ('baru','ditinjau','selesai')",
            name="ck_kasus_status",
        ),
    )


class AuditTrail(Base):
    """Audit trail logging all human decisions and review actions."""
    __tablename__ = "jejak_audit"

    id = Column(String, primary_key=True, default=_new_id)
    kasus_id = Column(String, ForeignKey("kasus.id"), nullable=False)
    pengguna_id = Column(String, ForeignKey("pengguna.id"), nullable=True)
    aksi = Column(String, nullable=False)
    objek = Column(String, nullable=False)
    alasan = Column(Text, nullable=True)
    waktu = Column(String, nullable=False, default=_now_iso)


# ─────────────────────────────────────────────────────────────
# Feature 2: Recycled Video Tracker
# ─────────────────────────────────────────────────────────────


class VideoArchive(Base):
    """Original verified reference video archive.

    Stores perceptual hash fingerprints and public metadata only.
    Raw video files are NOT permanently stored (zero-retention privacy policy).
    """
    __tablename__ = "arsip_video"

    id = Column(String, primary_key=True, default=_new_id)
    judul = Column(String, nullable=False)
    tanggal_asli = Column(String, nullable=True)
    sumber = Column(String, nullable=True)
    tautan = Column(String, nullable=True)

    # Relationships
    frames = relationship("FrameHash", back_populates="arsip_video", cascade="all, delete-orphan")
    hasil = relationship("VideoResult", back_populates="arsip_video")

    def __repr__(self):
        return f"<VideoArchive(id={self.id!r}, title={self.judul!r})>"


class FrameHash(Base):
    """Perceptual hash per keyframe of an archived video.

    Stores 64-bit pHash (frequency-based) and dHash (gradient-based).
    The 'urutan' field (0-based) preserves the temporal sequence.
    """
    __tablename__ = "hash_frame"

    id = Column(String, primary_key=True, default=_new_id)
    arsip_video_id = Column(String, ForeignKey("arsip_video.id"), nullable=False)
    urutan = Column(Integer, nullable=False)
    hash = Column(String, nullable=False)  # 64-bit pHash hex
    dhash = Column(String, nullable=True)  # 64-bit dHash hex

    arsip_video = relationship("VideoArchive", back_populates="frames")

    def __repr__(self):
        return f"<FrameHash(archive={self.arsip_video_id!r}, seq={self.urutan})>"


class VideoResult(Base):
    """Investigation result comparing an input video against the archive."""
    __tablename__ = "hasil_video"

    id = Column(String, primary_key=True, default=_new_id)
    kasus_id = Column(String, ForeignKey("kasus.id"), nullable=False)
    arsip_video_id = Column(String, ForeignKey("arsip_video.id"), nullable=True)
    skor = Column(Float, nullable=True)
    frame_cocok = Column(Integer, nullable=True)
    frame_total = Column(Integer, nullable=True)
    keyakinan = Column(String, nullable=True)

    arsip_video = relationship("VideoArchive", back_populates="hasil")

    def __repr__(self):
        return f"<VideoResult(case={self.kasus_id!r}, score={self.skor})>"


# ─────────────────────────────────────────────────────────────
# Feature 1: Issue Clarification
# ─────────────────────────────────────────────────────────────


class Clarification(Base):
    __tablename__ = "klarifikasi"

    id = Column(String, primary_key=True, default=_new_id)
    klaim = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    ringkasan = Column(Text, nullable=True)
    tanggal = Column(String, nullable=True)
    sumber = Column(String, nullable=False)
    tautan = Column(String, nullable=True)


class ClarificationResult(Base):
    __tablename__ = "hasil_klarifikasi"

    id = Column(String, primary_key=True, default=_new_id)
    kasus_id = Column(String, ForeignKey("kasus.id"), nullable=False)
    klarifikasi_id = Column(String, ForeignKey("klarifikasi.id"), nullable=True)
    skor_kemiripan = Column(Float, nullable=True)
    status_hasil = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status_hasil IN ('sudah_diklarifikasi','ditemukan_mirip','belum_ditemukan')",
            name="ck_hasil_klarifikasi_status",
        ),
    )


class PublicClaim(Base):
    """Usulan klaim publik yang menunggu persetujuan admin.

    Klaim yang disetujui akan dipromosikan menjadi entri `klarifikasi`
    sehingga langsung bisa ditemukan oleh endpoint `/clarification/check`.
    """
    __tablename__ = "usulan_klaim"

    id = Column(String, primary_key=True, default=_new_id)
    klaim = Column(Text, nullable=False)
    ringkasan = Column(Text, nullable=True)
    kategori = Column(String, nullable=True)
    sumber = Column(String, nullable=True)
    tautan_sumber = Column(String, nullable=True)
    anonim = Column(Boolean, nullable=False, default=True)
    alias_pemesan = Column(String, nullable=True)
    status = Column(String, nullable=False, default="menunggu")
    catatan_review = Column(Text, nullable=True)
    dibuat_pada = Column(String, nullable=False, default=_now_iso)
    ditinjau_pada = Column(String, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('menunggu','disetujui','ditolak')",
            name="ck_usulan_klaim_status",
        ),
    )


# ─────────────────────────────────────────────────────────────
# Feature 3: Manipulation Technique Mapping
# ─────────────────────────────────────────────────────────────


class Technique(Base):
    __tablename__ = "teknik"

    id = Column(String, primary_key=True, default=_new_id)
    nama = Column(String, nullable=False, unique=True)
    definisi = Column(Text, nullable=False)


class TechniqueResult(Base):
    __tablename__ = "hasil_teknik"

    id = Column(String, primary_key=True, default=_new_id)
    kasus_id = Column(String, ForeignKey("kasus.id"), nullable=False)
    teknik_id = Column(String, ForeignKey("teknik.id"), nullable=False)
    skor = Column(Float, nullable=False)
    bukti = Column(Text, nullable=True)
    status_tinjau = Column(String, nullable=False, default="menunggu")

    __table_args__ = (
        CheckConstraint(
            "status_tinjau IN ('menunggu','diterima','diubah','diabaikan')",
            name="ck_hasil_teknik_status",
        ),
    )


# ─────────────────────────────────────────────────────────────
# Feature 5: Mitigation & Clarification Cards
# ─────────────────────────────────────────────────────────────


class MitigationCard(Base):
    __tablename__ = "kartu_klarifikasi"

    id = Column(String, primary_key=True, default=_new_id)
    kasus_id = Column(String, ForeignKey("kasus.id"), nullable=False, unique=True)
    klaim = Column(Text, nullable=False)
    berkas = Column(String, nullable=False)
    dibuat_pada = Column(String, nullable=False, default=_now_iso)


# ─────────────────────────────────────────────────────────────
# Backward-compatibility Aliases
# ─────────────────────────────────────────────────────────────
Pengguna = User
Kasus = Case
JejakAudit = AuditTrail
ArsipVideo = VideoArchive
HashFrame = FrameHash
HasilVideo = VideoResult
Klarifikasi = Clarification
HasilKlarifikasi = ClarificationResult
UsulanKlaim = PublicClaim
Teknik = Technique
HasilTeknik = TechniqueResult
KartuKlarifikasi = MitigationCard
