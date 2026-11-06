"""Backward-compatibility layer for database schema models.

Delegates directly to `src.db.models`.
"""

from .models import (
    AuditTrail,
    Base,
    Case,
    Clarification,
    ClarificationResult,
    FrameHash,
    MitigationCard,
    PublicClaim,
    Technique,
    TechniqueResult,
    User,
    VideoArchive,
    VideoResult,
    # Indonesian aliases
    ArsipVideo,
    HasilKlarifikasi,
    HasilTeknik,
    HasilVideo,
    HashFrame,
    JejakAudit,
    KartuKlarifikasi,
    Kasus,
    Klarifikasi,
    Pengguna,
    Teknik,
    UsulanKlaim,
)

__all__ = [
    "Base",
    "User",
    "Case",
    "AuditTrail",
    "VideoArchive",
    "FrameHash",
    "VideoResult",
    "Clarification",
    "ClarificationResult",
    "Technique",
    "TechniqueResult",
    "MitigationCard",
    "Pengguna",
    "Kasus",
    "JejakAudit",
    "ArsipVideo",
    "HashFrame",
    "HasilVideo",
    "Klarifikasi",
    "HasilKlarifikasi",
    "Teknik",
    "HasilTeknik",
    "KartuKlarifikasi",
]
