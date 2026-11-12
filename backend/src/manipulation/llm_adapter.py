"""LLM Adapter for Feature 3: Manipulation Technique Mapping.

Menggunakan Google Gemini API atau model LLM lain jika GEMINI_API_KEY tersedia.
Jika API key tidak disediakan atau panggilan gagal, modul secara halus (gracefully)
beralih ke heuristic engine bawaan tanpa menimbulkan error ke pengguna.
"""

import json
import logging
import os
from typing import Optional, Tuple, List
import httpx

from .schemas import EvidenceSpan, TechniqueScore
from .taxonomy import MANIPULATION_TAXONOMY
from .heuristics import detect_manipulation_heuristically

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Anda adalah analis intelijen siber forensik WARAZ (TNI AD Cyber Security Unit).
Tugas Anda adalah menganalisis teks klaim publik atau postingan media sosial untuk mendeteksi teknik manipulasi psikologis / rekayasa narasi berdasarkan taksonomi berikut:
1. framing_ancaman: Membingkai isu sebagai bahaya besar/kritis yang mengancam eksistensi.
2. urgensi_palsu: Menciptakan kesan darurat palsu (sebar sebelum dihapus, dll).
3. ilusi_konsensus: Mengklaim seolah semua orang/seluruh rakyat sudah sepakat.
4. pemicu_amarah: Memakai diksi provokatif dan membakar amarah emosional.
5. kambing_hitam: Menuduh kelompok tertentu (antek asing, dll) sebagai biang kerok tunggal (us-vs-them).
6. konteks_dipotong: Memotong kutipan atau rekaman video di luar konteks aslinya.
7. cherry_picking: Memilih data parsial untuk membenarkan narasi yang bias.
8. otoritas_palsu: Mencatut klaim dari figur/lembaga intelijen/ahli palsu.
9. whataboutism: Mengalihkan substansi masalah dengan menyalahkan pihak lain.

PENTING: Bedakan secara cermat antara teknik manipulasi dengan 'KRITIK SAH' terhadap pemerintah/kebijakan publik yang berbasis data atau pandangan umum yang wajar tanpa provokasi manipulatif.

Format KELUARAN HARUS berupa JSON murni tanpa markdown code block:
{
  "is_manipulative": boolean,
  "overall_manipulation_score": float (0.0 - 1.0),
  "summary": string,
  "classification": "Kritik Sah / Informatif" ATAU "Narasi Terindikasi Manipulatif",
  "techniques": [
    {
      "technique_id": string,
      "score": float (0.0 - 1.0),
      "evidences": [
        {"quote": string, "explanation": string}
      ]
    }
  ]
}
"""


async def analyze_with_llm(
    text: str, threshold: float = 0.45
) -> Optional[Tuple[List[TechniqueScore], float, str, bool, str]]:
    """Mencoba analisis menggunakan LLM Gemini jika API key tersedia.

    Returns None jika tidak ada API key atau request gagal.
    """
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not gemini_key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
    prompt = f"Analisis teks berikut secara objektif:\n\n\"\"\"\n{text}\n\"\"\""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT},
                    {"text": prompt},
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                logger.warning("Gemini API error %d: %s", resp.status_code, resp.text)
                return None

            data = resp.json()
            raw_text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            parsed = json.loads(raw_text)

            tech_map = {t["technique_id"]: t for t in parsed.get("techniques", [])}
            scored_techniques: List[TechniqueScore] = []

            for tech_id, tdef in MANIPULATION_TAXONOMY.items():
                match = tech_map.get(tech_id)
                score = float(match.get("score", 0.05)) if match else 0.05
                detected = score >= threshold

                raw_evidences = match.get("evidences", []) if match else []
                evidences = []
                for ev in raw_evidences:
                    quote = ev.get("quote", "")
                    if quote:
                        pos = text.find(quote)
                        evidences.append(
                            EvidenceSpan(
                                quote=quote,
                                start_char=pos if pos != -1 else None,
                                end_char=(pos + len(quote)) if pos != -1 else None,
                                explanation=ev.get("explanation"),
                            )
                        )

                scored_techniques.append(
                    TechniqueScore(
                        technique_id=tech_id,
                        technique_name=tdef["name_id"],
                        category=tdef["category"],
                        score=score,
                        detected=detected,
                        definition=tdef["definition"],
                        evidences=evidences if detected else [],
                    )
                )

            scored_techniques.sort(key=lambda x: x.score, reverse=True)
            overall_score = float(parsed.get("overall_manipulation_score", 0.15))
            summary = parsed.get("summary", "Analisis narasi selesai.")
            is_manipulative = bool(parsed.get("is_manipulative", False))

            return (
                scored_techniques,
                overall_score,
                summary,
                is_manipulative,
                "llm-gemini",
            )
    except Exception as exc:
        logger.warning("LLM analysis failed, fallback to heuristic: %s", exc)
        return None
