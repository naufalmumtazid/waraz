"""
WARAZ — Classification Dataset Generator
=========================================
Generates synthetic labeled datasets for Feature 1 / Feature 3
disinformation classification models.

Each record contains:
  - claim   : A realistic disinformation/hoax claim (Indonesian)
  - status  : One of {"hoaks", "disinformasi", "sebagian benar", "benar"}
  - summary : Short analyst note explaining the verdict
  - source  : Reference domain used for fact-checking
  - category: Thematic category of the claim (kebijakan / isu / sektor)

Output files (written to backend/data/contoh/):
  - waraz_classification_dataset.json
  - waraz_classification_dataset.csv

Usage (from project root):
    python -m backend.scripts.classification_datasets_generate
    # or
    python backend/scripts/classification_datasets_generate.py
"""

import csv
import itertools
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Output path
# ──────────────────────────────────────────────────────────────────────────────
_BACKEND_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = _BACKEND_DIR / "data" / "contoh"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

JSON_OUT = OUTPUT_DIR / "waraz_classification_dataset.json"
CSV_OUT = OUTPUT_DIR / "waraz_classification_dataset.csv"

# ──────────────────────────────────────────────────────────────────────────────
# Seed vocabulary
# ──────────────────────────────────────────────────────────────────────────────
kebijakan_list = [
    "kenaikan tarif pajak",
    "regulasi digital baru",
    "proyek infrastruktur strategis",
    "kebijakan energi nasional",
    "subsidi BBM",
    "penghapusan kartu prakerja",
    "kebijakan impor pangan",
    "regulasi media sosial",
    "kebijakan upah minimum",
    "program beasiswa nasional",
]

isu_list = [
    "ekonomi domestik",
    "kebebasan berpendapat",
    "reformasi belanja negara",
    "anggaran pendidikan",
    "pemilihan umum",
    "krisis pangan global",
    "privatisasi BUMN",
    "keamanan siber nasional",
    "perubahan iklim",
    "isu tenaga kerja asing",
]

sektor_list = [
    "ketenagakerjaan",
    "pendidikan tinggi",
    "layanan kesehatan",
    "ketahanan pangan",
    "sumber daya alam",
    "infrastruktur digital",
    "pertahanan dan keamanan",
    "pariwisata",
    "pertanian",
    "energi terbarukan",
]

domains = [
    "https://turnbackhoax.id",
    "https://kominfo.go.id/content/detail",
    "https://cekfakta.tempo.co",
    "https://liputan6.com/cek-fakta",
    "https://ajiindonesia.or.id/independen.or.id",
]

STATUSES = ["hoaks", "disinformasi", "sebagian benar", "benar"]

# ──────────────────────────────────────────────────────────────────────────────
# Template system
# Each template is (claim_template, status, summary_template, category)
# Placeholders: {kebijakan}, {isu}, {sektor}
# ──────────────────────────────────────────────────────────────────────────────
TEMPLATES: list[dict] = [
    # ── hoaks ──────────────────────────────────────────────────────────────
    {
        "claim": "Pemerintah diam-diam mencabut {kebijakan} tanpa sepengetahuan DPR.",
        "status": "hoaks",
        "summary": (
            "Tidak ada dokumen resmi yang mengonfirmasi pencabutan tersebut. "
            "Klaim beredar melalui pesan berantai tanpa sumber primer yang valid."
        ),
        "category": "kebijakan",
    },
    {
        "claim": "Dokumen bocor mengungkap anggaran khusus negara dialokasikan untuk "
                 "membayar buzzer pembuat hoaks terkait {sektor}.",
        "status": "hoaks",
        "summary": (
            "Dokumen yang beredar adalah draf komunikasi publik kementerian, "
            "namun narasinya dipintir seolah-olah dialokasikan khusus untuk produksi hoaks."
        ),
        "category": "sektor",
    },
    {
        "claim": "Viral: warga dipaksa bayar {kebijakan} dua kali lipat mulai bulan depan.",
        "status": "hoaks",
        "summary": (
            "Tidak ada peraturan resmi yang mengatur kenaikan ganda tersebut. "
            "Gambar yang digunakan sebagai bukti adalah hasil editan."
        ),
        "category": "kebijakan",
    },
    {
        "claim": "Pemerintah secara resmi merekrut influencer dan buzzer untuk membungkam "
                 "kritik publik di ruang digital.",
        "status": "hoaks",
        "summary": (
            "Pemerintah menegaskan kerja sama dengan influencer murni dilakukan untuk "
            "sosialisasi program pembangunan, bukan untuk membungkam kritik."
        ),
        "category": "isu",
    },
    # ── disinformasi ────────────────────────────────────────────────────────
    {
        "claim": "Buzzer sengaja memelintir data statistik sektor {sektor} untuk "
                 "menutupi evaluasi kinerja program.",
        "status": "disinformasi",
        "summary": (
            "Data yang dipaparkan lembaga resmi telah melalui audit independen, "
            "namun klaim yang beredar di media sosial menggunakan pemotongan grafik yang menyesatkan."
        ),
        "category": "sektor",
    },
    {
        "claim": "Laporan internal {isu} sengaja disembunyikan karena merugikan partai "
                 "berkuasa menjelang pemilu.",
        "status": "disinformasi",
        "summary": (
            "Laporan tersebut tersedia publik di situs resmi lembaga terkait. "
            "Narasi 'disembunyikan' dibuat untuk memancing ketidakpercayaan terhadap institusi."
        ),
        "category": "isu",
    },
    {
        "claim": "Data {kebijakan} yang dirilis pemerintah sengaja dimanipulasi agar terlihat "
                 "sukses sebelum pilkada.",
        "status": "disinformasi",
        "summary": (
            "Metodologi pengumpulan data mengikuti standar BPS. "
            "Klaim manipulasi muncul dari akun anonim tanpa bukti metodologis."
        ),
        "category": "kebijakan",
    },
    {
        "claim": "Jaringan buzzer terkoordinasi menyebarkan narasi palsu soal {sektor} "
                 "dengan pola unggahan identik di ratusan akun.",
        "status": "disinformasi",
        "summary": (
            "Analisis CIB (Coordinated Inauthentic Behavior) oleh peneliti independen "
            "mengonfirmasi pola koordinasi, namun konten dasar mengandung fakta yang diputarbalikkan."
        ),
        "category": "sektor",
    },
    # ── sebagian benar ──────────────────────────────────────────────────────
    {
        "claim": "Trending topik media sosial mengenai {isu} disetel sepenuhnya oleh "
                 "jaringan buzzer pesanan kelompok politik.",
        "status": "sebagian benar",
        "summary": (
            "Analisis media sosial mendeteksi lonjakan aktivitas akun terkoordinasi (CIB), "
            "namun tidak seluruhnya berasal dari satu pesanan tunggal."
        ),
        "category": "isu",
    },
    {
        "claim": "{kebijakan} memang naik, namun kenaikannya disebut jauh lebih besar "
                 "dari kenyataan yang berlaku.",
        "status": "sebagian benar",
        "summary": (
            "Kenaikan memang terjadi sesuai regulasi yang berlaku, "
            "namun angka yang viral dalam narasi tersebut dilebih-lebihkan hingga tiga kali lipat."
        ),
        "category": "kebijakan",
    },
    {
        "claim": "Anggaran sektor {sektor} memang dipotong, tetapi bukan untuk keperluan "
                 "kampanye seperti yang diklaim.",
        "status": "sebagian benar",
        "summary": (
            "Pemotongan anggaran memang terjadi akibat efisiensi fiskal, "
            "namun klaim bahwa dana dialihkan ke keperluan kampanye tidak didukung bukti apapun."
        ),
        "category": "sektor",
    },
    # ── benar ───────────────────────────────────────────────────────────────
    {
        "claim": "Pemerintah resmi mengumumkan {kebijakan} berlaku mulai kuartal berikutnya "
                 "melalui Peraturan Presiden.",
        "status": "benar",
        "summary": (
            "Peraturan Presiden telah diterbitkan dan dapat diakses di lembaran negara. "
            "Tidak ditemukan unsur manipulasi dalam penyebaran informasi ini."
        ),
        "category": "kebijakan",
    },
    {
        "claim": "Lembaga independen mengkonfirmasi adanya jaringan disinformasi terkait "
                 "{isu} dengan bukti forensik digital.",
        "status": "benar",
        "summary": (
            "Laporan lengkap tersedia dengan metodologi terbuka. "
            "Temuan divalidasi oleh tiga lembaga riset berbeda secara independen."
        ),
        "category": "isu",
    },
    {
        "claim": "Indeks kualitas sektor {sektor} meningkat berdasarkan laporan tahunan "
                 "BPS yang dipublikasikan secara transparan.",
        "status": "benar",
        "summary": (
            "Data BPS tersedia di portal resmi dengan metodologi yang dapat diverifikasi publik. "
            "Tidak ada indikasi manipulasi narasi dalam penyebaran informasi ini."
        ),
        "category": "sektor",
    },
]


# ──────────────────────────────────────────────────────────────────────────────
# Record generation
# ──────────────────────────────────────────────────────────────────────────────

def _fill(template: str, kebijakan: str, isu: str, sektor: str) -> str:
    return (
        template
        .replace("{kebijakan}", kebijakan)
        .replace("{isu}", isu)
        .replace("{sektor}", sektor)
    )


def generate_records(n: int = 200, seed: int = 42) -> list[dict]:
    """Generate *n* synthetic classification records.

    Each record is deterministically derived from the seed so the dataset is
    reproducible across runs.
    """
    random.seed(seed)
    records: list[dict] = []

    # Cycle through all combinations so coverage is broad even at low n
    combo_pool = list(itertools.product(kebijakan_list, isu_list, sektor_list))
    random.shuffle(combo_pool)
    combo_cycle = itertools.cycle(combo_pool)

    template_cycle = itertools.cycle(TEMPLATES)

    for i in range(n):
        tpl = next(template_cycle)
        kebijakan, isu, sektor = next(combo_cycle)
        domain = domains[i % len(domains)]

        records.append(
            {
                "id": i + 1,
                "claim": _fill(tpl["claim"], kebijakan, isu, sektor),
                "status": tpl["status"],
                "summary": tpl["summary"],
                "category": tpl["category"],
                "source": domain,
                "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            }
        )

    return records


# ──────────────────────────────────────────────────────────────────────────────
# Writers
# ──────────────────────────────────────────────────────────────────────────────

def write_json(records: list[dict], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"[OK] JSON  -> {path}  ({len(records)} records)")


def write_csv(records: list[dict], path: Path) -> None:
    if not records:
        return
    fieldnames = list(records[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"[OK] CSV   -> {path}  ({len(records)} records)")


# ──────────────────────────────────────────────────────────────────────────────
# CLI entrypoint
# ──────────────────────────────────────────────────────────────────────────────

def main(n: int = 200, seed: int = 42) -> None:
    print("WARAZ — Classification Dataset Generator")
    print(f"  Generating {n} records (seed={seed}) …")

    records = generate_records(n=n, seed=seed)

    # Status distribution summary
    from collections import Counter
    dist = Counter(r["status"] for r in records)
    print("  Status distribution:")
    for status, count in sorted(dist.items()):
        print(f"    {status:<18} {count:>4} records")

    write_json(records, JSON_OUT)
    write_csv(records, CSV_OUT)
    print("Done.")


if __name__ == "__main__":
    # Optional CLI args: python script.py <n> <seed>
    _n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    _seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    main(n=_n, seed=_seed)
