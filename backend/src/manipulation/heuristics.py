"""Pattern matching and heuristic engine for manipulation technique detection.

Berfungsi sebagai engine deterministik dan offline fallback yang kuat,
dapat dijalankan tanpa API key / ketergantungan jaringan eksternal.
"""

import re
from typing import List, Tuple
from .schemas import EvidenceSpan, TechniqueScore
from .taxonomy import MANIPULATION_TAXONOMY


def find_evidence_spans(text: str, indicators: List[str]) -> List[EvidenceSpan]:
    """Mencari kutipan bukti dalam teks berdasarkan indikator kata kunci dan pola."""
    spans: List[EvidenceSpan] = []
    text_lower = text.lower()
    seen_quotes = set()

    for pattern in indicators:
        idx = 0
        while True:
            pos = text_lower.find(pattern.lower(), idx)
            if pos == -1:
                break
            # Ambil potongan kalimat atau frasa utuh di sekitar indikator
            start = max(0, pos)
            end = min(len(text), pos + len(pattern))
            
            # Perluas sedikit ke batas kata jika memungkinkan
            quote = text[start:end]
            if quote.lower() not in seen_quotes:
                seen_quotes.add(quote.lower())
                spans.append(
                    EvidenceSpan(
                        quote=quote,
                        start_char=start,
                        end_char=end,
                        explanation=f"Frasa '{quote}' mengindikasikan pola manipulasi",
                    )
                )
            idx = pos + len(pattern)

    return spans


def score_technique_heuristically(
    technique_id: str, text: str, threshold: float
) -> TechniqueScore:
    """Menghitung skor heuristik kemunculan teknik manipulasi."""
    tech_def = MANIPULATION_TAXONOMY[technique_id]
    indicators = tech_def["indicators"]
    spans = find_evidence_spans(text, indicators)

    text_len = len(text.strip())
    match_count = len(spans)

    if match_count == 0:
        score = 0.05
    else:
        # Base score berbanding lurus dengan jumlah indikator yang terdeteksi
        base_score = 0.45 + min(0.50, match_count * 0.22)

        # Penguat konteks tambahan (tanda seru berulang, ALL-CAPS kata)
        has_exclamations = bool(re.search(r"!{2,}", text))
        caps_words = len(re.findall(r"\b[A-Z]{3,}\b", text))

        if (technique_id in ("urgensi_palsu", "pemicu_amarah", "framing_ancaman")) and has_exclamations:
            base_score = min(0.98, base_score + 0.12)
        if caps_words >= 2:
            base_score = min(0.98, base_score + 0.08)

        score = round(base_score, 2)

    detected = score >= threshold

    return TechniqueScore(
        technique_id=technique_id,
        technique_name=tech_def["name_id"],
        category=tech_def["category"],
        score=score,
        detected=detected,
        definition=tech_def["definition"],
        evidences=spans if detected else [],
    )


def detect_manipulation_heuristically(
    text: str, threshold: float = 0.45
) -> Tuple[List[TechniqueScore], float, str, bool]:
    """Mendeteksi seluruh 9 teknik manipulasi menggunakan rule-based engine.

    Returns:
        (techniques, overall_score, summary, is_manipulative)
    """
    results: List[TechniqueScore] = []
    detected_list: List[TechniqueScore] = []

    for tech_id in MANIPULATION_TAXONOMY.keys():
        score_obj = score_technique_heuristically(tech_id, text, threshold)
        results.append(score_obj)
        if score_obj.detected:
            detected_list.append(score_obj)

    # Urutkan berdasarkan skor tertinggi
    results.sort(key=lambda x: x.score, reverse=True)

    if detected_list:
        max_score = max(t.score for t in detected_list)
        avg_score = sum(t.score for t in detected_list) / len(detected_list)
        overall_score = round(min(0.98, max_score * 0.7 + avg_score * 0.3), 2)
        is_manipulative = True

        tech_names = [t.technique_name for t in detected_list]
        summary = (
            f"Terdeteksi {len(detected_list)} teknik manipulasi narasi: "
            f"{', '.join(tech_names)}. Narasi mengandung elemen provokasi atau pembingkaian tendensius."
        )
    else:
        overall_score = 0.12
        is_manipulative = False
        summary = (
            "Tidak terdeteksi indikator teknik manipulasi yang signifikan. "
            "Teks cenderung berbentuk kritik yang sah, opini wajar, atau informasi faktual."
        )

    return results, overall_score, summary, is_manipulative
