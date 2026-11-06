"""Core logic for Feature 1: Issue Clarification.

Responsibilities:
- Public claim submission (menunggu persetujuan admin).
- Similarity-based issue lookup against the `klarifikasi` basis.
- Admin review workflow (approve → promote into `klarifikasi`).
- Admin authentication against environment-configured credentials.
"""

import difflib
import logging
import secrets
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from ..db.models import Clarification, PublicClaim
from . import config

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize(text: str) -> str:
    """Lowercase plain-text normalization for similarity comparison."""
    return " ".join(text.lower().split()) if text else ""


def normalize_claim_status(value: Optional[str]) -> str:
    """Normalize claim classification values to the canonical WARAZ labels."""
    if not value:
        return "lainnya"

    cleaned = _normalize(value)
    if cleaned in {"sebagian benar", "sebagian_benar"}:
        return "menyesatkan"
    if cleaned in {"hoaks", "disinformasi", "benar", "menyesatkan", "lainnya"}:
        return cleaned
    return "lainnya"


def similarity(left: str, right: str) -> float:
    """Normalized string similarity in [0.0, 1.0]."""
    l, r = _normalize(left), _normalize(right)
    if not l or not r:
        return 0.0
    if l == r:
        return 1.0
    ratio = difflib.SequenceMatcher(None, l, r).ratio()
    # Partial containment bonus: short claims matching inside a longer issue.
    if l in r or r in l:
        ratio = max(ratio, min(len(l), len(r)) / max(len(l), len(r)))
    return round(ratio, 4)


def check_issue(db: Session, issue: str) -> Dict:
    """Evaluate an issue against the clarification knowledge base."""
    issue = (issue or "").strip()

    if not issue:
        return {
            "status_result": "tidak_ada_isi",
            "score": 0.0,
            "matches": [],
            "note": "Isu tidak berisi teks yang bisa diperiksa.",
        }

    rows: List[Clarification] = db.query(Clarification).all()

    scored: List[Dict] = []
    for row in rows:
        score = max(
            similarity(issue, row.klaim),
            similarity(issue, row.ringkasan or "") * 0.95,
        )
        if score > 0.0:
            scored.append(
                {
                    "id": row.id,
                    "claim": row.klaim,
                    "status": row.status,
                    "summary": row.ringkasan or "",
                    "date": row.tanggal or "",
                    "source": row.sumber,
                    "url": row.tautan or "",
                    "score": score,
                }
            )

    scored.sort(key=lambda m: m["score"], reverse=True)
    matches = scored[: config.MAX_MATCHES]
    best = scored[0]["score"] if scored else 0.0

    if best >= config.CONFIRMED_THRESHOLD:
        status_result = "sudah_diklarifikasi"
        note = "Isu ini sudah pernah diklarifikasi berdasarkan basis data WARAZ."
    elif best >= config.SIMILAR_THRESHOLD and matches:
        status_result = "ditemukan_mirip"
        note = "Ditemukan klarifikasi yang mirip dengan isu yang kamu masukkan."
    else:
        status_result = "belum_ditemukan"
        note = "Belum ada klarifikasi di basis data. Silakan ajukan klaim baru."
        matches = []

    return {
        "status_result": status_result,
        "score": best,
        "matches": matches,
        "note": note,
    }


def submit_claim(db: Session, payload: Dict) -> Dict:
    """Persist a public claim submission pending admin review."""
    claim = PublicClaim(
        klaim=payload["claim"],
        ringkasan=payload.get("summary"),
        kategori=payload.get("category") or "lainnya",
        sumber=payload.get("source") or "input_pengguna",
        tautan_sumber=payload.get("source_url"),
        anonim=bool(payload.get("anonymous", True)),
        alias_pemesan=payload.get("submitter_alias"),
        status=config.STATUS_CLAIM,
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    logger.info("Usulan klaim baru disimpan: %s", claim.id)
    return claim_to_dict(claim)


def claim_to_dict(claim: PublicClaim) -> Dict:
    """Serialize a PublicClaim into the public API shape."""
    return {
        "id": claim.id,
        "claim": claim.klaim,
        "summary": claim.ringkasan,
        "category": claim.kategori,
        "source": claim.sumber,
        "source_url": claim.tautan_sumber,
        "anonymous": bool(claim.anonim),
        "submitter_alias": claim.alias_pemesan,
        "status": claim.status,
        "review_note": claim.catatan_review,
        "created_at": claim.dibuat_pada,
        "reviewed_at": claim.ditinjau_pada,
    }


def list_pending_claims(db: Session) -> List[Dict]:
    """List all claims still awaiting admin review (oldest first)."""
    rows = (
        db.query(PublicClaim)
        .filter(PublicClaim.status == config.STATUS_CLAIM)
        .order_by(PublicClaim.dibuat_pada.asc())
        .all()
    )
    return [claim_to_dict(row) for row in rows]


def review_claim(
    db: Session,
    claim_id: str,
    decision: str,
    review_note: Optional[str],
) -> Dict:
    """Approve or reject a pending claim.

    Approved claims are promoted into the `klarifikasi` basis so they
    become discoverable via `/clarification/check`.
    """
    claim: Optional[PublicClaim] = db.get(PublicClaim, claim_id)
    if claim is None:
        return None
    if claim.status != config.STATUS_CLAIM:
        raise ValueError("Klaim ini sudah pernah ditinjau.")

    now = _now_iso()

    if decision == "approve":
        claim.status = config.STATUS_APPROVED
        claim.catatan_review = review_note
        claim.ditinjau_pada = now

        promoted = Clarification(
            klaim=claim.klaim,
            status=normalize_claim_status(claim.kategori),
            ringkasan=claim.ringkasan,
            tanggal=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            sumber=claim.sumber or "input_pengguna",
            tautan=claim.tautan_sumber,
        )
        db.add(promoted)
        logger.info("Klaim %s disetujui dan masuk basis klarifikasi.", claim_id)
    else:
        claim.status = config.STATUS_REJECTED
        claim.catatan_review = review_note
        claim.ditinjau_pada = now
        logger.info("Klaim %s ditolak admin.", claim_id)

    db.commit()
    db.refresh(claim)
    return claim_to_dict(claim)


# ─────────────────────────────────────────────────────────────
# Admin Authentication
# ─────────────────────────────────────────────────────────────


def verify_admin_credentials(email: str, password: str) -> Optional[str]:
    """Check admin credentials against env configuration.

    Returns the admin token on success, otherwise None.
    """
    expected_email = config.get_admin_email()
    expected_password = config.get_admin_password()

    email_ok = secrets.compare_digest(email.strip().lower(), expected_email.lower())
    password_ok = secrets.compare_digest(password or "", expected_password)

    if not (email_ok and password_ok):
        return None
    return config.get_admin_token()


def is_valid_admin_token(token: Optional[str]) -> bool:
    """Validate the x-admin-token header value."""
    return bool(token) and secrets.compare_digest(token, config.get_admin_token())
