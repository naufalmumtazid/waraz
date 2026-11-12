"""Taksonomi teknik manipulasi psikologis dan rekayasa narasi untuk WARAZ (Feature 3).

Taksonomi merujuk pada Dokumen Proposal dan Rancangan Teknologi WARAZ:
1. framing_ancaman (Framing Ancaman / Threat Framing)
2. urgensi_palsu (Urgensi Palsu / False Urgency)
3. ilusi_konsensus (Ilusi Konsensus / Illusion of Consensus)
4. pemicu_amarah (Pemicu Amarah / Outrage Triggering)
5. kambing_hitam (Kambing Hitam atau Us-vs-Them / Scapegoating & Polarization)
6. konteks_dipotong (Konteks Dihapus atau Dipotong / Decontextualization)
7. cherry_picking (Cherry-Picking Data / Selective Evidence)
8. otoritas_palsu (Otoritas Palsu / False Authority)
9. whataboutism (Whataboutism / Tu Quoque deflection)
"""

from typing import Dict, List, TypedDict


class TechniqueDefinition(TypedDict):
    id: str
    name: str
    name_id: str
    category: str
    definition: str
    indicators: List[str]
    example: str


MANIPULATION_TAXONOMY: Dict[str, TechniqueDefinition] = {
    "framing_ancaman": {
        "id": "framing_ancaman",
        "name": "Threat Framing",
        "name_id": "Framing Ancaman",
        "category": "Psikologis / Ketakutan",
        "definition": (
            "Membingkai peristiwa atau isu sebagai bahaya eksistensial, krisis besar, "
            "atau ancaman mengerikan untuk memicu kepanikan dan menekan pemikiran rasional."
        ),
        "indicators": [
            "awas bahaya", "negara terancam", "akan hancur", "bahaya laten",
            "kiamat", "musnah", "terancam punah", "serangan masif",
            "malapetaka", "waspada", "genting", "ancaman nyata",
            "darurat sipil", "diserang"
        ],
        "example": "Awas bahaya laten kedaulatan kita dihancurkan dari dalam oleh antek asing!",
    },
    "urgensi_palsu": {
        "id": "urgensi_palsu",
        "name": "False Urgency",
        "name_id": "Urgensi Palsu",
        "category": "Tekanan Waktu",
        "definition": (
            "Menciptakan kesan darurat palsu yang menuntut pembaca membagikan informasi "
            "atau bertindak seketika tanpa sempat memverifikasi kebenaran klaim."
        ),
        "indicators": [
            "sebelum dihapus", "viralkan segera", "sebar luas sekarang", "detik ini juga",
            "jangan tunggu besok", "sebelum terlambat", "cepat forward", "sebar ke semua grup",
            "broadcast penting", "darurat", "info A1", "wajib share"
        ],
        "example": "Sebarkan segera sebelum postingan ini di-takedown oleh penguasa!",
    },
    "ilusi_konsensus": {
        "id": "ilusi_konsensus",
        "name": "Illusion of Consensus",
        "name_id": "Ilusi Konsensus",
        "category": "Tekanan Sosial",
        "definition": (
            "Menciptakan persepsi semu seolah mayoritas rakyat, seluruh warga, "
            "atau netizen telah sepakat mendukung atau menolak suatu narasi tertentu."
        ),
        "indicators": [
            "seluruh rakyat tahu", "semua orang sepakat", "netizen bersatu", "satu indonesia sudah paham",
            "tak ada yang percaya lagi", "semua elemen menolak", "jutaan massa kompak",
            "sudah jadi rahasia umum", "semua mata tertuju", "seluruh dunia sepakat"
        ],
        "example": "Semua orang juga sudah tahu dan sepakat kalau kebijakan itu hanya akal-akalan!",
    },
    "pemicu_amarah": {
        "id": "pemicu_amarah",
        "name": "Outrage Triggering",
        "name_id": "Pemicu Amarah",
        "category": "Emosional",
        "definition": (
            "Memilih diksi kasar, menghina, atau provokatif yang dirancang khusus "
            "untuk membakar emosi amarah publik, memicu kebencian, atau memancing keributan."
        ),
        "indicators": [
            "kebangetan", "biadab", "pengkhianat bangsa", "kurang ajar",
            "laknat", "tikus kantor", "rejim bobrok", "membodohi rakyat",
            "penindas", "culas", "menjijikkan", "tak punya hati", "dungu"
        ],
        "example": "Biadab sekali tindakan aparat boneka ini, benar-benar pengkhianat rakyat!",
    },
    "kambing_hitam": {
        "id": "kambing_hitam",
        "name": "Scapegoating & Polarization (Us-vs-Them)",
        "name_id": "Kambing Hitam / Us-vs-Them",
        "category": "Polarisasi",
        "definition": (
            "Menyalahkan satu kelompok tertentu (suku, agama, oposisi, pihak asing, buzzer) "
            "sebagai biang kerok tunggal dan mempertentangkan 'kita yang suci vs mereka yang jahat'."
        ),
        "indicators": [
            "antek asing", "kelompok mereka", "kaum cebong", "kaum kadrun",
            "biang kerok kekacauan", "mereka sengaja menjatuhkan kita", "musuh bersama",
            "antek aseng", "kelompok penyusup", "kelompok radikal", "antek rezim"
        ],
        "example": "Semua kekacauan ekonomi ini jelas ulah kelompok oposisi dan antek asing yang tidak senang negeri ini damai.",
    },
    "konteks_dipotong": {
        "id": "konteks_dipotong",
        "name": "Decontextualization",
        "name_id": "Konteks Dihapus / Dipotong",
        "category": "Manipulasi Bukti",
        "definition": (
            "Memotong kutipan pidato, potongan video, atau menghilangkan latar belakang penting "
            "sehingga makna aslinya berbalik 180 derajat dari maksud sebenarnya."
        ),
        "indicators": [
            "video sengaja dipotong", "rekaman ini membuktikan", "hanya diperlihatkan sebagian",
            "tanpa penjelasan awal", "di luar konteks", "dibalik faktanya",
            "tonton bagian menit ini", "mengaku sendiri secara terang-terangan"
        ],
        "example": "Dengarkan sendiri video detik ke-10, pejabat itu mengaku tidak peduli pada nasib rakyat miskin!",
    },
    "cherry_picking": {
        "id": "cherry_picking",
        "name": "Cherry-Picking Data",
        "name_id": "Cherry-Picking Data",
        "category": "Manipulasi Data",
        "definition": (
            "Memilih sebagian kecil angka, grafik, atau sampel yang menguntungkan narasi disinformasi "
            "sambil dengan sengaja menyembunyikan tren keseluruhan atau data komprehensif."
        ),
        "indicators": [
            "lihat saja angka hari ini", "bukti grafik merosot", "hanya mengambil data dari",
            "fakta membuktikan 90% gagal", "satu kasus ini membuktikan seluruhnya hancur",
            "data ini sengaja ditutupi", "angka yang disembunyikan"
        ],
        "example": "Lihat saja data penurunan 2% di bulan lalu, membuktikan seluruh program swasembada 5 tahun gagal total!",
    },
    "otoritas_palsu": {
        "id": "otoritas_palsu",
        "name": "False Authority",
        "name_id": "Otoritas Palsu",
        "category": "Kredibilitas Semu",
        "definition": (
            "Mencatut nama jenderal, profesor, dokter spesialis, lembaga intelijen, "
            "atau ahli anonim yang tidak pernah memberikan pernyataan tersebut."
        ),
        "indicators": [
            "menurut dokter spesialis terkenal", "bocoran dari perwira tinggi", "profesor intelijen membocorkan",
            "ahli militer ternama dunia", "laporan rahasia badan intelijen", "orang dalam istana membenarkan",
            "petinggi unesa", "pakar ternama mengonfirmasi", "kata intel A1"
        ],
        "example": "Orang dalam badan intelijen membocorkan ada operasi rahasia pengalihan isu nasional minggu depan.",
    },
    "whataboutism": {
        "id": "whataboutism",
        "name": "Whataboutism",
        "name_id": "Whataboutism / Pengalihan Isu",
        "category": "Distraksi Debat",
        "definition": (
            "Mengalihkan substansi kritik atau tuduhan dengan membalikkan tudingan "
            "pada kesalahan pihak lain yang tidak relevan ('Kenapa kamu diam saat rezim sebelumnya...?')."
        ),
        "indicators": [
            "kenapa diam saja waktu", "bagaimana dengan kasus", "giliran kelompok itu kok tidak disoal",
            "kenapa baru ribut sekarang", "waktu zaman mereka lebih parah", "kok tidak teriak waktu",
            "munafik giliran pihak sana diam", "kenapa tidak bahas"
        ],
        "example": "Giliran kasus ini kalian ribut, tapi kenapa waktu skandal triliunan pihak sebelah kemarin kalian semua bungkam?",
    },
}

# Contoh teks demo (beberapa manipulative, beberapa kritik sah / kontra-contoh)
DEMO_PRESETS = [
    {
        "id": "preset_krisis_urgensi",
        "title": "Urgensi Palsu & Framing Ancaman",
        "text": "DARURAT SIPIL! Sebarkan segera ke seluruh grup sebelum dihapus pihak berwenang! Negara kita sedang terancam invasi aseng dari dalam, malam ini juga kita harus bergerak!",
        "expected_labels": ["urgensi_palsu", "framing_ancaman"],
        "is_manipulation": True,
    },
    {
        "id": "preset_otoritas_polaritas",
        "title": "Otoritas Palsu & Us-vs-Them",
        "text": "Orang dalam badan intelijen membocorkan bahwa semua kekacauan ini adalah ulah antek asing dan kelompok oposisi yang berniat menggulingkan stabilitas nasional.",
        "expected_labels": ["otoritas_palsu", "kambing_hitam"],
        "is_manipulation": True,
    },
    {
        "id": "preset_kritik_sah",
        "title": "Kontra-Contoh: Kritik Sah Terhadap Kebijakan (Bukan Manipulasi)",
        "text": "Berdasarkan rilis resmi Badan Pusat Statistik triwulan III 2026, realisasi serapan anggaran infrastruktur baru mencapai 64%. Kementerian terkait perlu meningkatkan transparansi tender dan evaluasi pengawasan lapangan.",
        "expected_labels": [],
        "is_manipulation": False,
    },
    {
        "id": "preset_whataboutism_konsensus",
        "title": "Ilusi Konsensus & Whataboutism",
        "text": "Seluruh rakyat Indonesia sudah sepakat dan tahu siapa dalangnya. Kenapa media bungkam dan kenapa baru ribut sekarang, giliran skandal kubu sana kok kalian diam seribu bahasa?",
        "expected_labels": ["ilusi_konsensus", "whataboutism"],
        "is_manipulation": True,
    },
    {
        "id": "preset_potongan_konteks",
        "title": "Konteks Dipotong & Pemicu Amarah",
        "text": "Biadab sekali menteri ini! Tonton sendiri rekaman video ini bagaimana pejabat angkuh tersebut terang-terangan menertawakan penderitaan para buruh tani!",
        "expected_labels": ["pemicu_amarah", "konteks_dipotong"],
        "is_manipulation": True,
    },
]
