"""Pydantic schemas for Feature 3: Manipulation Technique Mapping."""

from typing import List, Optional
from pydantic import BaseModel, Field


class EvidenceSpan(BaseModel):
    """Spesifikasi kutipan bukti teks yang terdeteksi manipulasi."""
    quote: str = Field(..., description="Kutipan teks asli yang menjadi bukti manipulasi")
    start_char: Optional[int] = Field(None, description="Indeks karakter awal kutipan dalam teks")
    end_char: Optional[int] = Field(None, description="Indeks karakter akhir kutipan dalam teks")
    explanation: Optional[str] = Field(None, description="Penjelasan mengapa kutipan ini mengindikasikan teknik terkait")


class TechniqueScore(BaseModel):
    """Skor dan detail deteksi untuk satu teknik manipulasi spesifik."""
    technique_id: str = Field(..., description="ID teknik manipulasi (misal: 'framing_ancaman')")
    technique_name: str = Field(..., description="Nama teknik (Bahasa Indonesia)")
    category: str = Field(..., description="Kategori psikologis / narasi")
    score: float = Field(..., ge=0.0, le=1.0, description="Skor probabilitas / keyakinan (0.0 sampai 1.0)")
    detected: bool = Field(..., description="Apakah teknik ini melampaui ambang batas keyakinan")
    definition: str = Field(..., description="Definisi teknik manipulasi")
    evidences: List[EvidenceSpan] = Field(default_factory=list, description="Kutipan bukti pada teks asli")


class AnalysisRequest(BaseModel):
    """Permintaan analisis teknik manipulasi narasi."""
    text: str = Field(..., min_length=5, description="Teks klaim, postingan medsos, atau caption video yang akan dianalisis")
    confidence_threshold: float = Field(
        default=0.45, ge=0.1, le=0.9, description="Ambang batas keyakinan deteksi (default 0.45)"
    )
    case_id: Optional[str] = Field(None, description="ID kasus investigasi jika dihubungkan dengan modul kasus WARAZ")


class AnalysisResponse(BaseModel):
    """Hasil analisis terstruktur teknik manipulasi."""
    text: str
    is_manipulative: bool = Field(..., description="Apakah teks secara keseluruhan dinilai manipulatif")
    overall_manipulation_score: float = Field(..., ge=0.0, le=1.0, description="Skor manipulasi keseluruhan (0.0 - 1.0)")
    summary: str = Field(..., description="Ringkasan analisis narasi")
    classification: str = Field(..., description="'Kritik Sah / Informatif' atau 'Narasi Terindikasi Manipulatif'")
    confidence_threshold: float
    detected_techniques_count: int
    techniques: List[TechniqueScore]
    engine_used: str = Field(..., description="'rule-based-heuristics' atau 'llm-gemini' atau 'cached'")
    analyzed_at: str
    case_id: Optional[str] = None


class OverrideLabelRequest(BaseModel):
    """Permintaan analis untuk mengubah atau mengabaikan label teknik."""
    technique_id: str
    status: str = Field(..., pattern="^(diterima|diubah|diabaikan)$")
    analyst_note: Optional[str] = None


class PresetExample(BaseModel):
    """Preset contoh kasus pengujian untuk antarmuka demo."""
    id: str
    title: str
    text: str
    expected_labels: List[str]
    is_manipulation: bool
