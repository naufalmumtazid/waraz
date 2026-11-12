"""Service layer for Feature 3: Manipulation Technique Mapping."""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from .schemas import (
    AnalysisRequest,
    AnalysisResponse,
    OverrideLabelRequest,
    PresetExample,
    TechniqueScore,
)
from .taxonomy import MANIPULATION_TAXONOMY, DEMO_PRESETS
from .heuristics import detect_manipulation_heuristically
from .llm_adapter import analyze_with_llm

try:
    from ..db.skema import Kasus, Pengguna, Teknik, HasilTeknik
except ImportError:
    from src.db.skema import Kasus, Pengguna, Teknik, HasilTeknik

logger = logging.getLogger(__name__)

# Simple in-memory cache for fast response and demo reproducibility
_ANALYSIS_CACHE: Dict[str, AnalysisResponse] = {}


def _get_cache_key(text: str, threshold: float) -> str:
    cleaned = text.strip().lower()
    return hashlib.sha256(f"{cleaned}:{threshold}".encode("utf-8")).hexdigest()


def ensure_techniques_seeded(db: Session) -> None:
    """Memastikan taksonomi teknik terdaftar di tabel `teknik`."""
    try:
        for tech_id, tdef in MANIPULATION_TAXONOMY.items():
            existing = db.query(Teknik).filter(Teknik.nama == tdef["name_id"]).first()
            if not existing:
                tech = Teknik(
                    id=f"tek-{tech_id}",
                    nama=tdef["name_id"],
                    definisi=tdef["definition"],
                )
                db.add(tech)
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning("Gagal seed teknik ke database: %s", exc)


async def analyze_text(req: AnalysisRequest, db: Optional[Session] = None) -> AnalysisResponse:
    """Menganalisis teks menggunakan hybrid LLM + Heuristic Engine."""
    cache_key = _get_cache_key(req.text, req.confidence_threshold)
    if cache_key in _ANALYSIS_CACHE:
        cached_res = _ANALYSIS_CACHE[cache_key].model_copy()
        cached_res.engine_used = "cached"
        return cached_res

    # Coba LLM jika key ada, jika tidak fallback ke heuristic
    llm_result = await analyze_with_llm(req.text, req.confidence_threshold)
    
    if llm_result:
        techniques, overall_score, summary, is_manipulative, engine_name = llm_result
    else:
        techniques, overall_score, summary, is_manipulative = detect_manipulation_heuristically(
            req.text, req.confidence_threshold
        )
        engine_name = "rule-based-heuristics"

    detected_count = sum(1 for t in techniques if t.detected)
    classification = (
        "Narasi Terindikasi Manipulatif"
        if is_manipulative and detected_count > 0
        else "Kritik Sah / Informatif"
    )

    now_iso = datetime.now(timezone.utc).isoformat()

    response = AnalysisResponse(
        text=req.text,
        is_manipulative=is_manipulative and detected_count > 0,
        overall_manipulation_score=overall_score,
        summary=summary,
        classification=classification,
        confidence_threshold=req.confidence_threshold,
        detected_techniques_count=detected_count,
        techniques=techniques,
        engine_used=engine_name,
        analyzed_at=now_iso,
        case_id=req.case_id,
    )

    # Simpan ke cache
    _ANALYSIS_CACHE[cache_key] = response

    # Jika ada session db dan case_id, simpan hasil teknik ke database
    if db and req.case_id:
        try:
            ensure_techniques_seeded(db)
            case = db.query(Kasus).filter(Kasus.id == req.case_id).first()
            if case:
                for t in techniques:
                    if t.detected:
                        tech_db = db.query(Teknik).filter(Teknik.nama == t.technique_name).first()
                        if tech_db:
                            bukti_str = json.dumps([e.model_dump() for e in t.evidences], ensure_ascii=False)
                            res_entry = HasilTeknik(
                                kasus_id=case.id,
                                teknik_id=tech_db.id,
                                skor=t.score,
                                bukti=bukti_str,
                                status_tinjau="menunggu",
                            )
                            db.add(res_entry)
                db.commit()
        except Exception as exc:
            db.rollback()
            logger.warning("Gagal menyimpan hasil teknik ke kasus: %s", exc)

    return response


def get_taxonomy_info() -> List[Dict]:
    """Mengembalikan daftar lengkap taksonomi teknik manipulasi."""
    return list(MANIPULATION_TAXONOMY.values())


def get_presets() -> List[PresetExample]:
    """Mengembalikan daftar preset contoh pengujian."""
    return [PresetExample(**p) for p in DEMO_PRESETS]


def override_technique_status(
    case_id: str,
    technique_id: str,
    req: OverrideLabelRequest,
    db: Session,
) -> Dict:
    """Mengubah status peninjauan teknik oleh analis (human-in-the-loop)."""
    ensure_techniques_seeded(db)
    tech_def = MANIPULATION_TAXONOMY.get(technique_id)
    if not tech_def:
        raise ValueError(f"Teknik '{technique_id}' tidak ditemukan dalam taksonomi.")

    tech_db = db.query(Teknik).filter(Teknik.nama == tech_def["name_id"]).first()
    if not tech_db:
        raise ValueError(f"Teknik record tidak ditemukan di DB.")

    result_entry = (
        db.query(HasilTeknik)
        .filter(HasilTeknik.kasus_id == case_id, HasilTeknik.teknik_id == tech_db.id)
        .first()
    )

    if not result_entry:
        result_entry = HasilTeknik(
            kasus_id=case_id,
            teknik_id=tech_db.id,
            skor=0.0,
            bukti=req.analyst_note or "Label manual ditambahkan oleh analis",
            status_tinjau=req.status,
        )
        db.add(result_entry)
    else:
        result_entry.status_tinjau = req.status
        if req.analyst_note:
            result_entry.bukti = f"{result_entry.bukti or ''} [Catatan Analis: {req.analyst_note}]"

    db.commit()
    db.refresh(result_entry)
    return {
        "status": "sukses",
        "kasus_id": case_id,
        "teknik_id": technique_id,
        "status_tinjau": result_entry.status_tinjau,
    }
