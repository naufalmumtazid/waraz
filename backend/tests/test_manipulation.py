"""Unit and integration tests for Feature 3: Manipulation Technique Mapping."""

import pytest
from fastapi.testclient import TestClient

from main import app
from src.manipulation.taxonomy import MANIPULATION_TAXONOMY, DEMO_PRESETS
from src.manipulation.heuristics import (
    score_technique_heuristically,
    detect_manipulation_heuristically,
)

client = TestClient(app)


def test_taxonomy_endpoint():
    """Memverifikasi ketersediaan 9 teknik manipulasi dalam taksonomi."""
    response = client.get("/api/v1/manipulation/taxonomy")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9
    tech_ids = {item["id"] for item in data}
    assert "framing_ancaman" in tech_ids
    assert "urgensi_palsu" in tech_ids
    assert "ilusi_konsensus" in tech_ids
    assert "pemicu_amarah" in tech_ids
    assert "kambing_hitam" in tech_ids
    assert "konteks_dipotong" in tech_ids
    assert "cherry_picking" in tech_ids
    assert "otoritas_palsu" in tech_ids
    assert "whataboutism" in tech_ids


def test_presets_endpoint():
    """Memverifikasi ketersediaan preset uji coba demo."""
    response = client.get("/api/v1/manipulation/presets")
    assert response.status_code == 200
    presets = response.json()
    assert len(presets) >= 4
    # Memastikan ada contoh kritik sah
    safe_presets = [p for p in presets if not p["is_manipulation"]]
    assert len(safe_presets) >= 1


def test_heuristics_threat_and_urgency():
    """Uji deteksi kombinasi framing ancaman dan urgensi palsu."""
    text = "DARURAT SIPIL! Sebarkan segera ke seluruh grup sebelum dihapus pihak berwenang! Negara kita sedang terancam invasi aseng!"
    techniques, overall_score, summary, is_manipulative = detect_manipulation_heuristically(text, threshold=0.45)

    assert is_manipulative is True
    assert overall_score > 0.5

    detected_ids = {t.technique_id for t in techniques if t.detected}
    assert "urgensi_palsu" in detected_ids
    assert "framing_ancaman" in detected_ids

    # Memastikan evidence quote diekstraksi
    urgency_tech = next(t for t in techniques if t.technique_id == "urgensi_palsu")
    assert len(urgency_tech.evidences) > 0


def test_heuristics_legitimate_criticism():
    """Uji kontra-contoh: kritik sah tidak boleh dicap manipulatif."""
    safe_text = (
        "Berdasarkan rilis resmi Badan Pusat Statistik triwulan III 2026, realisasi serapan anggaran "
        "infrastruktur baru mencapai 64%. Kementerian terkait perlu meningkatkan transparansi tender dan evaluasi pengawasan lapangan."
    )
    techniques, overall_score, summary, is_manipulative = detect_manipulation_heuristically(safe_text, threshold=0.45)

    assert is_manipulative is False
    assert overall_score < 0.35
    detected_count = sum(1 for t in techniques if t.detected)
    assert detected_count == 0


def test_api_analyze_endpoint_manipulation():
    """Uji endpoint API /analyze dengan payload manipulatif."""
    payload = {
        "text": "Biadab sekali tindakan aparat ini! Tonton sendiri rekaman video ini bagaimana pejabat angkuh menertawakan rakyat!",
        "confidence_threshold": 0.40,
    }
    response = client.post("/api/v1/manipulation/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["is_manipulative"] is True
    assert data["detected_techniques_count"] >= 1
    assert data["classification"] == "Narasi Terindikasi Manipulatif"
    assert "pemicu_amarah" in [t["technique_id"] for t in data["techniques"] if t["detected"]]


def test_api_analyze_endpoint_safe_criticism():
    """Uji endpoint API /analyze dengan kritik konstruktif."""
    payload = {
        "text": "Data BPS menunjukkan laju inflasi bahan pokok terkendali di level 2,5%. Pemerintah daerah diharapkan menjaga rantai pasok distribusi.",
        "confidence_threshold": 0.45,
    }
    response = client.post("/api/v1/manipulation/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["is_manipulative"] is False
    assert data["classification"] == "Kritik Sah / Informatif"
    assert data["detected_techniques_count"] == 0


def test_api_analyze_validation_error():
    """Uji validasi jika teks terlalu pendek."""
    response = client.post("/api/v1/manipulation/analyze", json={"text": "halo"})
    assert response.status_code == 422 or response.status_code == 400


def test_root_endpoint_includes_feature_3():
    """Uji endpoint root backend menyertakan F3."""
    response = client.get("/")
    assert response.status_code == 200
    fitur = response.json().get("fitur_tersedia", [])
    assert any("F3: Peta Teknik Manipulasi" in f for f in fitur)
