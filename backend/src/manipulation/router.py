"""FastAPI Router for Feature 3: Manipulation Technique Mapping.

Endpoints:
- POST /api/v1/manipulation/analyze         → Menganalisis teks narasi terhadap 9 teknik manipulasi
- GET  /api/v1/manipulation/taxonomy        → Mendapatkan daftar taksonomi teknik beserta indikatornya
- GET  /api/v1/manipulation/presets         → Mendapatkan preset contoh uji (termasuk kontra-contoh)
- POST /api/v1/manipulation/cases/{case_id}/override → Analis override label / ambang batas
"""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db.koneksi import get_db
from .schemas import (
    AnalysisRequest,
    AnalysisResponse,
    OverrideLabelRequest,
    PresetExample,
)
from . import service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/manipulation",
    tags=["Manipulation Technique Mapping (F3)"],
)


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analisis Teks & Peta Teknik Manipulasi",
)
async def analyze_manipulation(
    req: AnalysisRequest,
    db: Session = Depends(get_db),
):
    """Menganalisis teks narasi berita / postingan sosial media.

    Mengembalikan JSON terstruktur dengan skor keyakinan untuk 9 teknik manipulasi,
    kutipan bukti (spans), dan ringkasan klasifikasi (Kritik Sah vs Manipulatif).
    """
    if len(req.text.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teks terlalu pendek untuk dianalisis (minimal 5 karakter).",
        )

    try:
        res = await service.analyze_text(req, db=db)
        return res
    except Exception as exc:
        logger.exception("Gagal memproses analisis manipulasi: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan saat memproses analisis: {str(exc)}",
        )


@router.get(
    "/taxonomy",
    response_model=List[Dict[str, Any]],
    summary="Daftar Taksonomi Teknik Manipulasi",
)
def get_taxonomy():
    """Mengambil 9 taksonomi teknik manipulasi standar WARAZ."""
    return service.get_taxonomy_info()


@router.get(
    "/presets",
    response_model=List[PresetExample],
    summary="Preset Contoh Kasus Uji & Kontra-Contoh",
)
def get_presets():
    """Mengambil preset kalimat uji untuk kemudahan demonstrasi."""
    return service.get_presets()


@router.post(
    "/cases/{case_id}/override",
    summary="Override atau Ubah Label Teknik oleh Analis",
)
def override_label(
    case_id: str,
    req: OverrideLabelRequest,
    db: Session = Depends(get_db),
):
    """Memungkinkan analis mengabaikan atau menyetujui label teknik tertentu."""
    try:
        return service.override_technique_status(case_id, req.technique_id, req, db)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.exception("Gagal override status teknik: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal memperbarui status peninjauan teknik.",
        )
