"""FastAPI router für Feature 1: Issue Clarification.

Endpoints:
- POST /api/v1/clarification/check          → cek isu terhadap basis klarifikasi
- POST /api/v1/clarification/submit         → usulan klaim publik (anonim opsional)
- POST /api/v1/clarification/admin/login    → autentikasi admin
- GET  /api/v1/clarification/admin/claims   → daftar usulan menunggu review
- POST /api/v1/clarification/admin/claims/{id}/review → setujui / tolak usulan
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db.koneksi import get_db
from . import service
from .config import STATUS_CLAIM

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/clarification", tags=["Issue Clarification (F1)"])

# ─────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────


class IssueCheckRequest(BaseModel):
    issue: str


class ClaimSubmitRequest(BaseModel):
    claim: str
    summary: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    category: Optional[str] = None
    anonymous: bool = True
    submitter_alias: Optional[str] = None


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class ClaimReviewRequest(BaseModel):
    decision: str  # "approve" | "reject"
    review_note: Optional[str] = None


# ─────────────────────────────────────────────────────────────
# Public endpoints
# ─────────────────────────────────────────────────────────────


@router.post("/check", summary="Cek isu terhadap basis klarifikasi")
def api_check_issue(payload: IssueCheckRequest, db: Session = Depends(get_db)):
    """Mencocokkan isu dengan dataset klarifikasi menggunakan similarity."""
    return service.check_issue(db, payload.issue)


@router.post("/submit", summary="Kirim usulan klaim publik")
def api_submit_claim(payload: ClaimSubmitRequest, db: Session = Depends(get_db)):
    """Menyimpan usulan klaim baru dengan status 'menunggu'.

    Klaim hanya akan masuk ke basis klarifikasi setelah admin menyetujuinya.
    """
    if not payload.claim.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Klaim tidak boleh kosong.",
        )

    saved = service.submit_claim(db, payload.model_dump())
    return {"message": "Klaim berhasil dikirim dan menunggu persetujuan admin.", **saved}


# ─────────────────────────────────────────────────────────────
# Admin endpoints
# ─────────────────────────────────────────────────────────────


@router.post("/admin/login", summary="Login admin")
def api_admin_login(payload: AdminLoginRequest):
    """Memverifikasi email & password admin dari konfigurasi WARAZ_ADMIN_*."""
    token = service.verify_admin_credentials(payload.email, payload.password)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password admin salah.",
        )
    return {"token": token, "message": "Login admin berhasil."}


def _require_admin(x_admin_token: Optional[str]) -> None:
    """Dependency guard untuk endpoint berheader x-admin-token."""
    if not service.is_valid_admin_token(x_admin_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token admin tidak valid. Silakan login ulang.",
        )


@router.get("/admin/claims", summary="Daftar usulan klaim yang menunggu review")
def api_list_pending_claims(x_admin_token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    _require_admin(x_admin_token)
    return service.list_pending_claims(db)


@router.post(
    "/admin/claims/{claim_id}/review",
    summary="Setujui atau tolak usulan klaim",
)
def api_review_claim(
    claim_id: str,
    payload: ClaimReviewRequest,
    x_admin_token: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    _require_admin(x_admin_token)
    if payload.decision not in ("approve", "reject"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="decision harus 'approve' atau 'reject'.",
        )

    try:
        updated = service.review_claim(db, claim_id, payload.decision, payload.review_note)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usulan klaim tidak ditemukan.")

    return updated
