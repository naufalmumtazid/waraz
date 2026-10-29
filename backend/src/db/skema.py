"""SQLAlchemy models untuk WARAZ — sesuai skema di agent.md bagian 6.

Fokus F2: arsip_video, hash_frame, hasil_video.
Tabel lain (pengguna, kasus, jejak_audit, dll.) juga didefinisikan
agar foreign key berfungsi dan anggota tim lain bisa langsung pakai.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    CheckConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def _new_id() -> str:
    """Generate UUID baru sebagai string."""
    return str(uuid.uuid4())


def _now_iso() -> str:
    """Waktu sekarang dalam format ISO 8601 UTC."""
    return datetime.now(timezone.utc).isoformat()


class Base(DeclarativeBase):
    pass


# ──────────────────────────────────────────────
# Tabel umum
# ──────────────────────────────────────────────


class Pengguna(Base):
    __tablename__ = "pengguna"

    id = Column(String, primary_key=True, default=_new_id)
    nama = Column(String, nullable=False)
    peran = Column(String, nullable=False)
    dibuat_pada = Column(String, nullable=False, default=_now_iso)

    __table_args__ = (
        CheckConstraint("peran IN ('pengguna','analis')", name="ck_pengguna_peran"),
    )


class Kasus(Base):
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


class JejakAudit(Base):
    __tablename__ = "jejak_audit"

    id = Column(String, primary_key=True, default=_new_id)
    kasus_id = Column(String, ForeignKey("kasus.id"), nullable=False)
    pengguna_id = Column(String, ForeignKey("pengguna.id"), nullable=True)
    aksi = Column(String, nullable=False)
    objek = Column(String, nullable=False)
    alasan = Column(Text, nullable=True)
    waktu = Column(String, nullable=False, default=_now_iso)


# ──────────────────────────────────────────────
# F2: Pelacak Video Daur Ulang
# ──────────────────────────────────────────────


class ArsipVideo(Base):
    """Video asli yang disimpan di arsip.

    Menyimpan metadata dan tautan, BUKAN salinan video
    (sesuai batasan keras #8 di agent.md).
    """

    __tablename__ = "arsip_video"

    id = Column(String, primary_key=True, default=_new_id)
    judul = Column(String, nullable=False)
    tanggal_asli = Column(String, nullable=True)
    sumber = Column(String, nullable=True)
    tautan = Column(String, nullable=True)

    # Relationship
    frames = relationship("HashFrame", back_populates="arsip_video", cascade="all, delete-orphan")
    hasil = relationship("HasilVideo", back_populates="arsip_video")

    def __repr__(self):
        return f"<ArsipVideo(id={self.id!r}, judul={self.judul!r})>"


class HashFrame(Base):
    """Hash perceptual per keyframe dari video arsip.

    Menyimpan pHash hex 64-bit per frame.
    Urutan (0-based) menunjukkan posisi frame dalam video.
    """

    __tablename__ = "hash_frame"

    id = Column(String, primary_key=True, default=_new_id)
    arsip_video_id = Column(String, ForeignKey("arsip_video.id"), nullable=False)
    urutan = Column(Integer, nullable=False)
    hash = Column(String, nullable=False)  # pHash hex 64-bit
    dhash = Column(String, nullable=True)  # dHash hex 64-bit untuk ketahanan teks/banner overlay

    # Relationship
    arsip_video = relationship("ArsipVideo", back_populates="frames")

    def __repr__(self):
        return f"<HashFrame(arsip={self.arsip_video_id!r}, urutan={self.urutan})>"


class HasilVideo(Base):
    """Hasil pencocokan video yang di-upload user dengan arsip.

    Terkait dengan kasus (analisis).
    """

    __tablename__ = "hasil_video"

    id = Column(String, primary_key=True, default=_new_id)
    kasus_id = Column(String, ForeignKey("kasus.id"), nullable=False)
    arsip_video_id = Column(String, ForeignKey("arsip_video.id"), nullable=True)
    skor = Column(Float, nullable=True)
    frame_cocok = Column(Integer, nullable=True)
    frame_total = Column(Integer, nullable=True)
    keyakinan = Column(String, nullable=True)

    # Relationship
    arsip_video = relationship("ArsipVideo", back_populates="hasil")

    def __repr__(self):
        return f"<HasilVideo(kasus={self.kasus_id!r}, skor={self.skor})>"


# ──────────────────────────────────────────────
# F1: Cek Klarifikasi Isu (stub untuk FK)
# ──────────────────────────────────────────────


class Klarifikasi(Base):
    __tablename__ = "klarifikasi"

    id = Column(String, primary_key=True, default=_new_id)
    klaim = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    ringkasan = Column(Text, nullable=True)
    tanggal = Column(String, nullable=True)
    sumber = Column(String, nullable=False)
    tautan = Column(String, nullable=True)


class HasilKlarifikasi(Base):
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


# ──────────────────────────────────────────────
# F3: Peta Teknik Manipulasi (stub untuk FK)
# ──────────────────────────────────────────────


class Teknik(Base):
    __tablename__ = "teknik"

    id = Column(String, primary_key=True, default=_new_id)
    nama = Column(String, nullable=False, unique=True)
    definisi = Column(Text, nullable=False)


class HasilTeknik(Base):
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


# ──────────────────────────────────────────────
# F5: Mitigasi (stub untuk FK)
# ──────────────────────────────────────────────


class KartuKlarifikasi(Base):
    __tablename__ = "kartu_klarifikasi"

    id = Column(String, primary_key=True, default=_new_id)
    kasus_id = Column(String, ForeignKey("kasus.id"), nullable=False, unique=True)
    klaim = Column(Text, nullable=False)
    berkas = Column(String, nullable=False)
    dibuat_pada = Column(String, nullable=False, default=_now_iso)
