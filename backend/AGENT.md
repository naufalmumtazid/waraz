# AGENTS.md: Spesifikasi Proyek WARAZ

Dokumen ini ditujukan untuk coding agent. Baca seluruhnya sebelum menulis kode. Jika ada hal yang tidak jelas, bertanyalah (lihat bagian 16) dan jangan mengarang.

## 0. Cara memakai dokumen ini

1. Bangun per fase (bagian 14). Selesaikan satu alur utama yang berjalan sebelum menambah fitur.
2. Prioritaskan purwarupa yang **berjalan dan bisa didemokan** di atas kelengkapan fitur.
3. Patuhi batasan di bagian 3. Batasan itu berasal dari aturan lomba dan tidak boleh dilanggar walau diminta pengguna.
4. Setiap hasil analisis wajib membawa **alasan/bukti** dan **tingkat keyakinan**.
5. Jangan menambah dependensi berat (database server, Kafka, Spark, Kubernetes).
6. Jangan menulis klaim di antarmuka yang belum benar-benar diimplementasikan (misalnya "berkas dihapus setelah analisis" hanya boleh ada jika kodenya menghapus berkas).

## 1. Konteks

- **Lomba:** Kartika Cyber Hackathon 2026, penyelenggara PUSSIBERAD dan CODEPOLITAN.
- **Kategori:** 04 Siber Sosial (pemantauan dan analisis ruang siber sosial untuk mendeteksi ancaman non-teknis).
- **Nama proyek:** WARAZ. Tagline: "Deteksi Koordinasi, Klarifikasi Narasi".
- **Tim:** 3 orang.
- **Batas submission:** 15 November 2026, 23:59 WIB. Targetkan submit 14 November.
- **Wajib dikumpulkan:** link karya publik yang bisa dicoba juri tanpa instalasi, thumbnail 1200x630 (maks 500 KB), maksimal 5 screenshot, video maks 10 menit (YouTube), slide penjelasan.
- **Kriteria penilaian:** relevansi dan manfaat untuk TNI AD 25%, inovasi teknis 25%, fungsionalitas purwarupa 25%, kelayakan implementasi 15%, dokumentasi 10%.
- **Final (jika lolos):** presentasi 10 menit di Jakarta, 24 November 2026.

## 2. Ringkasan produk

WARAZ adalah **lapisan analisis**, bukan pengumpul data. Pengguna atau analis memasukkan data (teks, video, CSV anonim). Sistem membantu memeriksa narasi dan menyiapkan tindak lanjut. Ada dua jenis pengguna:

| Pengguna | Aktivitas |
|---|---|
| `pengguna` (siapa saja) | Layar **Cek Cepat**: unggah video atau tempel teks/tautan, lihat hasil |
| `analis` | **Dashboard**, **Tinjau dan Koreksi**, unggah CSV massal, setujui tindak lanjut |

### Lima fitur

| # | Fitur | Ringkas |
|---|---|---|
| F1 | Cek Klarifikasi Isu | Mencocokkan isu dengan basis klarifikasi terkurasi dan menampilkan status serta sumber |
| F2 | Pelacak Video Daur Ulang | Mencocokkan keyframe video dengan arsip hash untuk menemukan video lama yang dipakai ulang |
| F3 | Peta Teknik Manipulasi | Melabeli teknik rekayasa narasi (urgensi palsu, framing ancaman, dll.) dengan kutipan bukti |
| F4 | Pendeteksi dan Peta Koordinasi Jaringan | Graf koordinasi akun anonim, peran akun, meteran konsensus, kandidat sumber awal, prediksi volume 6-12 jam |
| F5 | Mitigasi dan Tindak Lanjut | Rekomendasi tindakan berbasis aturan, daftar akun tertanda anonim, paket bukti, Kartu Klarifikasi, persetujuan analis |

## 3. Batasan keras (jangan dilanggar)

1. **Tidak ada scraping** media sosial dan tidak ada kode yang mengambil data akun nyata. Data masuk lewat unggahan atau data simulasi.
2. **Tidak ada data pribadi pihak ketiga.** Semua akun adalah ID anonim (`node_0001`) atau simulasi. Jangan simpan nama, nomor telepon, atau identitas nyata.
3. **Semua data demo berlabel "DATA SIMULASI"** di antarmuka.
4. **Manusia memutuskan.** Tidak ada tindakan otomatis ke platform, akun, atau pihak luar. Setiap tindakan memerlukan persetujuan analis dan dicatat di jejak audit.
5. **Bahasa antarmuka netral:** gunakan "indikasi amplifikasi terkoordinasi", "kandidat sumber awal", "akun tertanda berdasarkan indikasi". Jangan gunakan "pelaku", "dalang", atau vonis "buzzer".
6. **Tidak ada fitur membuat akun palsu, konten penyamaran, atau buzzer tandingan.**
7. **Tidak ada kunci API di repositori atau demo publik.** Baca dari variabel lingkungan. Demo publik memakai hasil yang sudah di-cache dan/atau model lokal.
8. **Arsip video hanya menyimpan hash dan metadata plus tautan**, bukan salinan video.
9. **Data sintetis tidak boleh memuat unsur SARA, pornografi, ujaran kebencian, atau tokoh/institusi nyata yang dipalsukan.** Skenario fiktif (misalnya satuan fiktif).
10. **Basis klarifikasi menyimpan ringkasan pendek dan tautan**, bukan salinan artikel. Catat sumber dan tanggal.
11. **Model bahasa tidak boleh memberi vonis dari ingatannya sendiri.** Pada F1 ia hanya merangkum hasil pencarian. Jika tidak ada sumber, tampilkan "belum ditemukan". Hasil "belum ditemukan" tidak berarti benar.
12. **Atribusi komponen pihak ketiga** (pustaka, model, data) dicatat di `docs/ATRIBUSI.md`.

## 4. Stack (sudah diputuskan)

| Lapisan | Pilihan utama | Cadangan |
|---|---|---|
| Bahasa | Python 3.11+ | |
| Antarmuka | Streamlit | React (hanya jika ada waktu) |
| Layanan | Fungsi Python dipanggil langsung dari Streamlit | FastAPI bila perlu dipisah |
| Video | ffmpeg, OpenCV, imagehash (pHash, dHash) | |
| Embedding teks | sentence-transformers (model multibahasa) | rapidfuzz/BM25 untuk kata kunci |
| LLM (F3, ringkasan F1) | API LLM dengan keluaran JSON, validasi Pydantic | Ollama (model lokal), atau klasifikator scikit-learn di atas embedding |
| Koordinasi dan graf | NumPy, Pandas, SciPy, scikit-learn, datasketch (MinHash), NetworkX | python-igraph |
| GNN (OPSIONAL) | PyTorch, PyTorch Geometric (GraphSAGE/GAT) | Lewati jika ablation tidak menunjukkan manfaat |
| Visual | Plotly, PyVis (grafik jaringan) | Cytoscape.js |
| Penyimpanan | SQLite (skema bagian 6), Parquet/DuckDB untuk data simulasi besar | |
| Dokumen | Pillow (kartu PNG), ReportLab atau WeasyPrint (paket bukti PDF) | |
| Pengemasan | Docker, `requirements.txt`, Makefile | |

Cek kompatibilitas versi PyTorch dan PyTorch Geometric sebelum mengunci `requirements.txt`. Jangan mengarang nomor versi; gunakan yang terpasang dan teruji.

## 5. Struktur repositori

```
waraz/
  AGENTS.md
  README.md
  Makefile                 # make setup | make seed | make demo | make eval | make test
  requirements.txt
  Dockerfile
  .streamlit/config.toml   # tema gelap (lihat bagian 11)
  data/
    contoh/                # CSV dan klip demo kecil (disertakan di repo)
    arsip_video/           # klip fiktif rekaman tim (tidak di-commit jika besar)
    cache/                 # hasil LLM dan model untuk demo offline
    waraz.db               # SQLite (dibuat oleh make seed)
  src/
    db/                    # skema.sql, koneksi, seed
    klarifikasi/           # F1
    video/                 # F2
    teknik/                # F3
    jaringan/              # F4: simulator, graf, koordinasi, sumber_awal, prediksi, gnn (opsional)
    tindak_lanjut/         # F5: aturan, paket_bukti, kartu, persetujuan
    audit/                 # jejak audit JSONL + tabel
    evaluasi/              # metrik dan skrip
  app/
    main.py                # Streamlit: navigasi
    halaman/               # cek_cepat.py, dashboard.py, tinjau.py, kartu.py
    komponen/              # bar_teknik, meteran, grafik_jaringan, dll.
    aset/                  # font, templat kartu
  tests/
  docs/                    # ATRIBUSI.md, ETIKA.md, EVALUASI.md
```

## 6. Skema database (SQLite)

Tulis ke `src/db/skema.sql`. ID adalah teks (UUID). Aktifkan `PRAGMA foreign_keys = ON`.

```sql
CREATE TABLE pengguna (
  id TEXT PRIMARY KEY,
  nama TEXT NOT NULL,
  peran TEXT NOT NULL CHECK (peran IN ('pengguna','analis')),
  dibuat_pada TEXT NOT NULL
);

CREATE TABLE kasus (
  id TEXT PRIMARY KEY,
  pengguna_id TEXT NOT NULL REFERENCES pengguna(id),
  judul TEXT NOT NULL,
  ringkasan TEXT,
  tingkat_risiko TEXT CHECK (tingkat_risiko IN ('rendah','sedang','tinggi')),
  keyakinan TEXT CHECK (keyakinan IN ('rendah','sedang','tinggi')),
  status TEXT NOT NULL DEFAULT 'baru' CHECK (status IN ('baru','ditinjau','selesai')),
  dibuat_pada TEXT NOT NULL
);

CREATE TABLE jejak_audit (
  id TEXT PRIMARY KEY,
  kasus_id TEXT NOT NULL REFERENCES kasus(id),
  pengguna_id TEXT REFERENCES pengguna(id),   -- NULL jika aksi sistem
  aksi TEXT NOT NULL,       -- 'disarankan','diterima','diubah','diabaikan','disetujui','diekspor'
  objek TEXT NOT NULL,      -- mis. 'hasil_teknik:<id>'
  alasan TEXT,
  waktu TEXT NOT NULL
);

CREATE TABLE kartu_klarifikasi (
  id TEXT PRIMARY KEY,
  kasus_id TEXT NOT NULL UNIQUE REFERENCES kasus(id),
  klaim TEXT NOT NULL,
  berkas TEXT NOT NULL,
  dibuat_pada TEXT NOT NULL
);

-- F1
CREATE TABLE klarifikasi (
  id TEXT PRIMARY KEY,
  klaim TEXT NOT NULL,
  status TEXT NOT NULL,     -- 'hoaks','disinformasi','menyesatkan','benar','lainnya'
  ringkasan TEXT,
  tanggal TEXT,
  sumber TEXT NOT NULL,
  tautan TEXT
);
CREATE TABLE hasil_klarifikasi (
  id TEXT PRIMARY KEY,
  kasus_id TEXT NOT NULL REFERENCES kasus(id),
  klarifikasi_id TEXT REFERENCES klarifikasi(id),  -- NULL jika belum ditemukan
  skor_kemiripan REAL,
  status_hasil TEXT NOT NULL CHECK (status_hasil IN ('sudah_diklarifikasi','ditemukan_mirip','belum_ditemukan'))
);

-- F2
CREATE TABLE arsip_video (
  id TEXT PRIMARY KEY,
  judul TEXT NOT NULL,
  tanggal_asli TEXT,
  sumber TEXT,
  tautan TEXT
);
CREATE TABLE hash_frame (
  id TEXT PRIMARY KEY,
  arsip_video_id TEXT NOT NULL REFERENCES arsip_video(id),
  urutan INTEGER NOT NULL,
  hash TEXT NOT NULL        -- pHash hex 64-bit
);
CREATE TABLE hasil_video (
  id TEXT PRIMARY KEY,
  kasus_id TEXT NOT NULL REFERENCES kasus(id),
  arsip_video_id TEXT REFERENCES arsip_video(id),  -- NULL jika tidak cocok
  skor REAL,
  frame_cocok INTEGER,
  frame_total INTEGER,
  keyakinan TEXT
);

-- F3
CREATE TABLE teknik (
  id TEXT PRIMARY KEY,
  nama TEXT NOT NULL UNIQUE,   -- slug taksonomi
  definisi TEXT NOT NULL
);
CREATE TABLE hasil_teknik (
  id TEXT PRIMARY KEY,
  kasus_id TEXT NOT NULL REFERENCES kasus(id),
  teknik_id TEXT NOT NULL REFERENCES teknik(id),
  skor REAL NOT NULL,
  bukti TEXT,
  status_tinjau TEXT NOT NULL DEFAULT 'menunggu' CHECK (status_tinjau IN ('menunggu','diterima','diubah','diabaikan'))
);

-- F4
CREATE TABLE klaster (
  id TEXT PRIMARY KEY,
  kasus_id TEXT NOT NULL REFERENCES kasus(id),
  skor_koordinasi REAL NOT NULL,
  jumlah_akun INTEGER NOT NULL,
  ciri TEXT
);
CREATE TABLE akun (
  id TEXT PRIMARY KEY,         -- ID anonim, mis. node_0412
  klaster_id TEXT REFERENCES klaster(id),
  label_anonim TEXT NOT NULL,
  peran_jaringan TEXT CHECK (peran_jaringan IN ('seeder','amplifier','jembatan','organik'))
);
CREATE TABLE postingan (
  id TEXT PRIMARY KEY,
  kasus_id TEXT NOT NULL REFERENCES kasus(id),
  akun_id TEXT NOT NULL REFERENCES akun(id),
  induk_id TEXT REFERENCES postingan(id),
  waktu TEXT NOT NULL,
  teks TEXT,
  tipe TEXT NOT NULL CHECK (tipe IN ('post','reply','repost'))
);
CREATE TABLE kandidat_sumber (
  id TEXT PRIMARY KEY,
  kasus_id TEXT NOT NULL REFERENCES kasus(id),
  akun_id TEXT NOT NULL REFERENCES akun(id),
  peringkat INTEGER NOT NULL,
  skor REAL NOT NULL,
  keyakinan TEXT
);
CREATE TABLE prediksi (
  id TEXT PRIMARY KEY,
  kasus_id TEXT NOT NULL REFERENCES kasus(id),
  jam_ke INTEGER NOT NULL,     -- 1..12
  volume INTEGER NOT NULL,
  batas_bawah INTEGER NOT NULL,
  batas_atas INTEGER NOT NULL,
  metode TEXT NOT NULL         -- 'eksponensial' | 'hawkes'
);

-- F5
CREATE TABLE rekomendasi (
  id TEXT PRIMARY KEY,
  kasus_id TEXT NOT NULL REFERENCES kasus(id),
  jenis TEXT NOT NULL,         -- 'kartu_klarifikasi','prebunking','eskalasi','pemantauan','laporan_platform'
  status TEXT NOT NULL DEFAULT 'disarankan' CHECK (status IN ('disarankan','disetujui','ditolak','diekspor')),
  disetujui_oleh TEXT REFERENCES pengguna(id),
  disetujui_pada TEXT
);
CREATE TABLE akun_tertanda (
  id TEXT PRIMARY KEY,
  rekomendasi_id TEXT NOT NULL REFERENCES rekomendasi(id),
  akun_id TEXT NOT NULL REFERENCES akun(id),
  alasan TEXT NOT NULL,
  skor REAL
);
CREATE TABLE paket_bukti (
  id TEXT PRIMARY KEY,
  rekomendasi_id TEXT NOT NULL UNIQUE REFERENCES rekomendasi(id),
  berkas TEXT NOT NULL,
  format TEXT NOT NULL,        -- 'pdf' | 'json'
  dibuat_pada TEXT NOT NULL
);
```

## 7. Format dataset (CSV, semua fiktif dan anonim)

**`data/contoh/klarifikasi.csv`** (F1)
```
klaim,status,ringkasan,tanggal,sumber,tautan
"Latihan gabungan dibatalkan, warga diminta mengungsi",hoaks,"Jadwal latihan tetap berjalan sesuai rencana",2026-03-03,"Rilis satuan (simulasi)","https://contoh.id/klarifikasi/1"
```
Target: 50-100 entri (skenario fiktif plus tautan dan ringkasan pendek dari sumber publik).

**`data/contoh/arsip_video.csv`** (F2): `judul,tanggal_asli,sumber,tautan,berkas_lokal`. Hash frame dihitung otomatis oleh `make seed`, bukan diketik. Target: 10-30 klip fiktif rekaman tim, plus versi "daur ulang" (dipotong, dikompres, diberi teks).

**`data/contoh/postingan_simulasi.csv`** (F4)
```
id,akun_id,waktu,teks,tipe,induk_id,label_dasar
p_001,node_0412,2026-10-20 09:00:01,"Sebarkan sebelum dihapus!",post,,seeder
p_002,node_0987,2026-10-20 09:01:12,"Sebarkan sebelum dihapus!",repost,p_001,amplifier
```
`label_dasar` (seeder/amplifier/jembatan/organik) hanya dipakai untuk evaluasi, **tidak boleh dibaca oleh algoritma deteksi**.

**`data/contoh/label_teknik.csv`** (F3 dan evaluasi)
```
teks,teknik,keterangan
"Sebarkan sebelum dihapus!",urgensi_palsu,"Mendesak tanpa dasar"
"Kebijakan ini perlu ditinjau karena datanya belum lengkap",tidak_ada,"Kritik sah"
```
Target: 100-200 baris, termasuk banyak kontra-contoh `tidak_ada`. Satu baris boleh punya beberapa teknik (pisahkan dengan `|`).

**Format unggahan CSV analis** (anonim): `akun_id,waktu,teks,tipe,induk_id`.

## 8. Spesifikasi modul

Semua modul mengembalikan `dict` yang cocok dengan skema JSON di bawah, dan menyertakan `bukti` serta `keyakinan`. Simpan konstanta ambang di `src/<modul>/konfigurasi.py` agar mudah diatur.

### F1: Cek Klarifikasi Isu (`src/klarifikasi/`)

**Fungsi:** `cek_isu(teks: str) -> dict`

Langkah:
1. Normalisasi teks (huruf kecil, hapus URL dan emoji berlebih).
2. Embedding dengan sentence-transformers (model multibahasa). Hitung cosine terhadap embedding seluruh `klarifikasi.klaim` (hitung sekali, simpan di `data/cache`).
3. Ambil top-3. Aturan status (ambang dapat diatur):
   - skor >= `AMBANG_YAKIN` (awal 0.80): `sudah_diklarifikasi`
   - `AMBANG_MIRIP` (awal 0.60) <= skor < `AMBANG_YAKIN`: `ditemukan_mirip`
   - selain itu: `belum_ditemukan`
4. Cadangan: rapidfuzz jika embedding tidak tersedia.
5. Ringkasan opsional via LLM, dengan instruksi "hanya gunakan teks hasil di bawah; jangan menambah fakta". Jika LLM gagal, tampilkan `ringkasan` dari basis apa adanya.

Keluaran:
```json
{
  "status_hasil": "sudah_diklarifikasi",
  "skor_kemiripan": 0.91,
  "cocok": [{"klarifikasi_id": "...", "klaim": "...", "status": "hoaks",
             "ringkasan": "...", "tanggal": "2026-03-03", "sumber": "...", "tautan": "..."}],
  "catatan": "Belum ditemukan tidak berarti benar."
}
```

### F2: Pelacak Video Daur Ulang (`src/video/`)

**Fungsi:** `periksa_video(path: str) -> dict`

Langkah:
1. ffmpeg: ekstrak 1 frame per `INTERVAL_DETIK` (awal 2).
2. imagehash: hitung pHash tiap frame (64-bit).
3. Bandingkan dengan `hash_frame` memakai jarak Hamming (NumPy, vektorisasi dengan operasi XOR dan popcount).
4. Frame dianggap cocok jika jarak <= `AMBANG_HAMMING` (awal 10).
5. Kecocokan video dinyatakan jika minimal `MIN_BERURUTAN` (awal 3) frame cocok berurutan terhadap arsip yang sama. `skor = frame_cocok / frame_total`.
6. **Hapus berkas video sementara setelah diproses** (agar klaim privasi di UI benar) dan simpan hanya hash. Tulis uji yang membuktikan berkas terhapus.

Keluaran:
```json
{
  "status": "kemungkinan_daur_ulang",
  "skor": 0.92,
  "frame_cocok": 7, "frame_total": 8,
  "arsip": {"id": "...", "judul": "...", "tanggal_asli": "2026-03-03", "sumber": "...", "tautan": "..."},
  "keyakinan": "tinggi",
  "catatan": "Tidak ditemukan di arsip bukan berarti video asli."
}
```
`status` dapat berupa `kemungkinan_daur_ulang`, `tidak_ditemukan_di_arsip`, atau `tidak_dapat_diproses`.

### F3: Peta Teknik Manipulasi (`src/teknik/`)

**Fungsi:** `analisis_teknik(teks: str) -> dict`

Taksonomi (slug): `framing_ancaman`, `urgensi_palsu`, `ilusi_konsensus`, `pemicu_amarah`, `kambing_hitam`, `konteks_dihapus`, `cherry_picking`, `otoritas_palsu`, `whataboutism`. Simpan definisi di tabel `teknik`.

Langkah:
1. Bangun prompt: instruksi sistem berisi taksonomi dan definisi, beberapa contoh (few-shot) **termasuk contoh bukan manipulasi**, dan perintah mengembalikan JSON saja.
2. Validasi dengan Pydantic. Jika tidak valid, ulangi satu kali; jika masih gagal kembalikan `{"teknik": [], "galat": "tidak_dapat_dianalisis"}`.
3. Saring skor di bawah `AMBANG_TEKNIK` (awal 0.60). Temuan di bawah ambang tetap dikembalikan dengan bendera `di_bawah_ambang: true`.
4. Cache hasil berdasarkan hash teks di `data/cache`.
5. Cadangan offline: Ollama atau klasifikator scikit-learn di atas embedding yang dilatih dari `label_teknik.csv`.

Keluaran:
```json
{
  "teknik": [
    {"nama": "urgensi_palsu", "skor": 0.88, "bukti": "sebarkan sebelum dihapus!", "di_bawah_ambang": false}
  ],
  "teknik_dominan": "urgensi_palsu"
}
```
`bukti` harus berupa potongan persis dari teks masukan agar bisa disorot di UI.

### F4: Jaringan Koordinasi (`src/jaringan/`)

**Simulator** (`simulator.py`): `buat_simulasi(n_organik, n_terkoordinasi, skenario, seed) -> DataFrame`. Hasilkan postingan dengan kolom `label_dasar`. Skenario wajib: `rapi` (sinkron, teks hampir identik), `samar` (jeda acak, parafrase), `lonjakan_organik` (banyak akun bereaksi pada kejadian nyata, **bukan** koordinasi). Gunakan seed tetap agar hasil reprodusibel. Teks sintetis harus bebas SARA.

**Pipa analisis** (`analisis_jaringan(df) -> dict`):
1. **Graf temporal:** node = akun; edge berbobot dari (a) posting teks mirip dalam jendela `JENDELA_MENIT` (awal 5), (b) reply/repost, (c) kemiripan teks (MinHash Jaccard atau cosine embedding).
2. **Koordinasi (garis dasar, wajib):** skor per pasangan akun dari kombinasi sinkronisasi waktu dan kemiripan teks; klastering DBSCAN atau agglomerative atas matriks jarak. Klaster dengan skor >= `AMBANG_KOORDINASI` ditandai terkoordinasi.
3. **Peran akun:** `seeder` (muncul paling awal di klaster/kaskade), `amplifier` (anggota klaster sinkron), `jembatan` (menghubungkan klaster terkoordinasi ke komunitas organik, ukur dengan betweenness), `organik` (sisanya).
4. **Meteran konsensus:** `sumber_independen = jumlah akun di luar klaster terkoordinasi + jumlah klaster terkoordinasi`. `rasio_independensi = sumber_independen / total_akun`.
5. **Kandidat sumber awal:** rekonstruksi pohon kaskade dari `induk_id` dan waktu. Skor = kombinasi berbobot peringkat waktu paling awal dan rumor centrality (versi log). Kembalikan top-3 dengan skor ternormalisasi dan keyakinan.
6. **Prediksi 6-12 jam:** hitung deret volume per jam. Garis dasar: ekstrapolasi eksponensial dari laju pertumbuhan terakhir. Pembanding: proses Hawkes sederhana (kernel eksponensial, parameter lewat `scipy.optimize`). Pita ketidakpastian 80% dari bootstrap residu. Kembalikan kedua metode.
7. **GNN (opsional, kerjakan terakhir):** GraphSAGE/GAT untuk klasifikasi peran/koordinasi. Latih pada sebagian simulasi, uji pada simulasi lain. **Wajib ablation** terhadap garis dasar; jika tidak lebih baik, jangan dijadikan jalur utama dan catat hasilnya jujur di `docs/EVALUASI.md`.

Keluaran:
```json
{
  "klaster_terkoordinasi": [{"id": "k1", "jumlah_akun": 2100, "skor_koordinasi": 0.91,
                             "ciri": "posting dalam jendela 3 menit, 87% teks mirip"}],
  "meteran": {"akun_total": 3812, "sumber_independen": 410, "rasio_independensi": 0.11, "keyakinan": "sedang"},
  "peran": {"node_0412": "seeder"},
  "kandidat_sumber": [{"akun_id": "node_0412", "peringkat": 1, "skor": 0.67}],
  "prediksi": [{"jam_ke": 6, "volume": 18500, "batas_bawah": 12000, "batas_atas": 27000, "metode": "hawkes"}],
  "catatan": "Indikasi koordinasi, bukan vonis. Koordinasi organik juga mungkin."
}
```

### F5: Mitigasi dan Tindak Lanjut (`src/tindak_lanjut/`)

**Aturan** disimpan di `src/tindak_lanjut/aturan.yaml` dan dievaluasi dengan Python (tanpa model rumit):
```yaml
- id: R1
  jika: {risiko: tinggi, video_daur_ulang: true}
  sarankan: [kartu_klarifikasi, prebunking, eskalasi]
- id: R2
  jika: {koordinasi_terindikasi: true, keyakinan: sedang}
  sarankan: [pemantauan, laporan_platform]
- id: R3
  jika: {hanya_teknik_manipulasi: true}
  sarankan: [prebunking]
```

Fungsi:
- `sarankan(kasus_id) -> list[dict]`: menghasilkan baris `rekomendasi` berstatus `disarankan` dan mencatat aksi sistem ke jejak audit.
- `setujui(rekomendasi_id, pengguna_id)`: hanya peran `analis`; mengubah status, mencatat audit.
- `susun_akun_tertanda(rekomendasi_id)`: dari klaster terkoordinasi; isi `akun_id` (anonim), `alasan`, `skor`. Teks antarmuka: "akun tertanda berdasarkan indikasi".
- `buat_paket_bukti(rekomendasi_id)`: ekspor PDF dan JSON berisi ringkasan kasus, temuan yang **diterima** analis, bukti, daftar akun anonim, dan catatan keterbatasan. **WARAZ tidak mengirim ke pihak luar**; paket diunduh dan diserahkan manusia lewat kanal resmi.
- `buat_kartu(kasus_id)`: PNG dengan Pillow, hanya memuat temuan yang diterima analis. Isi: klaim, temuan penyebaran, teknik, kandidat sumber (tanpa identitas), informasi resmi (placeholder bila belum ada), catatan "dianalisis otomatis, ditinjau analis".
- `buat_draf_prebunking(kasus_id)`: templat pesan peringatan singkat yang merujuk hanya ke informasi resmi yang sudah diverifikasi; bila tidak ada, sisakan placeholder `[PERNYATAAN RESMI]`.

## 9. Jejak audit

Setiap perubahan status temuan, persetujuan, dan ekspor ditulis ke tabel `jejak_audit` **dan** ke `data/audit.jsonl` (satu baris JSON per kejadian: `waktu, kasus_id, pengguna_id, aksi, objek, alasan`). Layar Tinjau menampilkan linimasa dari tabel ini.

## 10. Layar antarmuka

Referensi visual (mockup): https://claude.ai/artifact/RQYqrFm2RtgD3ymaMXCkEH . Ikuti struktur dan teks Indonesianya, tidak harus piksel-sempurna.

1. **Cek Cepat** (semua pengguna): tab Video, Teks atau tautan, Data postingan CSV (analis). Area unggah video, kolom keterangan opsional, tombol **Periksa**, tombol **Coba kasus contoh**. Hasil: lencana status video, dua thumbnail berdampingan (video unggahan vs arsip), bar teknik dengan bukti disorot, status klarifikasi dan sumber, tombol **Buat Kartu Klarifikasi** dan **Kirim ke analis**.
2. **Dashboard analis:** ringkasan narasi dan lencana risiko, peta jaringan (merah terkoordinasi, biru organik, kuning jembatan, penanda kandidat sumber awal), meteran konsensus, bar teknik, tabel kandidat sumber awal, kurva prediksi dengan pita ketidakpastian.
3. **Tinjau dan Koreksi (analis):** daftar temuan dengan tombol Terima/Ubah/Abaikan, slider ambang keyakinan, panel jejak audit, tombol **Setujui dan Buat Kartu Klarifikasi**.
4. **Kartu Klarifikasi:** pratinjau PNG dan tombol unduh.

Aturan UI:
- Semua layar menampilkan lencana **DATA SIMULASI** saat memakai data contoh.
- **"Coba kasus contoh" harus memuat kasus lengkap tanpa unggahan apa pun** (juri harus bisa mencoba langsung).
- Setiap temuan menampilkan skor, bukti, dan keyakinan.
- Kontras teks minimal terbaca di tema gelap; target sentuh minimal 44 px.

## 11. Tema

Atur di `.streamlit/config.toml` dan CSS ringan.

| Token | Nilai |
|---|---|
| Latar | `#0b0f14` |
| Permukaan | `#141a22` |
| Garis | `#232c38` |
| Teks | `#e8ebef` |
| Teks redup | `#9ba6b4` |
| Aksen merah | `#ff5c61` |
| Biru (organik) | `#5aa9ff` |
| Kuning (jembatan/peringatan) | `#f5b84a` |
| Hijau (diterima) | `#6fd08c` |
| Font | Space Grotesk (UI), IBM Plex Mono (label dan angka) |

## 12. Evaluasi (`src/evaluasi/`, jalankan dengan `make eval`)

Hasilkan `docs/EVALUASI.md` berisi satu tabel jujur, **termasuk kasus gagal dan penyebabnya**. Jangan menyetel ambang demi angka bagus tanpa mencatatnya.

| Fitur | Metrik | Cara |
|---|---|---|
| F1 | presisi dan recall pencocokan klaim | set uji parafrase dan klaim di luar basis |
| F2 | presisi dan recall | klip asli, dipotong, dikompres, diberi teks, di luar arsip; catat kegagalan pada klip dicerminkan atau diubah warna |
| F3 | presisi, recall, F1 per teknik | `label_teknik.csv`, wajib menyertakan kontra-contoh kritik sah |
| F4 | presisi, recall, F1 koordinasi; top-1 dan top-3 sumber awal; MAE dan cakupan rentang prediksi; garis dasar vs GNN | simulasi dengan `label_dasar`, termasuk skenario `samar` dan `lonjakan_organik` |
| F5 | uji alur: saran, persetujuan, paket, kartu, audit | uji otomatis end-to-end |
| Sistem | waktu dari input sampai kartu jadi | stopwatch dalam skrip |

Pisahkan data latih dan uji untuk setiap evaluasi.

## 13. Pengujian

- `tests/` minimal: pencocokan F1 (parafrase), kecocokan F2 pada klip dipotong, validasi JSON F3 (termasuk kasus keluaran LLM rusak), determinisme simulator (seed sama menghasilkan data sama), peran analis diperlukan untuk `setujui`, berkas video sementara terhapus, paket bukti tidak memuat identitas selain ID anonim.
- `make test` harus lulus sebelum membuat rilis demo.

## 14. Fase dan pembagian kerja

Hari ini 28 Oktober 2026. Submit paling lambat 15 November 23:59 WIB, target 14 November.

| Tanggal | Fase | Hasil |
|---|---|---|
| 28-29 Okt | Persiapan | Repositori, instalasi teruji (ffmpeg, PyTorch/PyG bila perlu), skema DB, `make setup` jalan |
| 30 Okt - 3 Nov | Data dan versi pertama | Basis klarifikasi, arsip video demo, simulator, set label; F1, F2, F3, F4 garis dasar versi awal |
| 4-5 Nov | Integrasi | Alur Cek Cepat sampai Kartu berjalan |
| 6-9 Nov | Lengkapi dan deploy | F4 (peran, prediksi), F5, dashboard, demo publik, GNN bila inti stabil |
| 10-12 Nov | Evaluasi dan dokumentasi | `docs/EVALUASI.md`, README, screenshot, thumbnail |
| 13 Nov | Bekukan fitur | Tidak ada fitur baru; rekam video, finalisasi slide |
| 14 Nov | Submit | |

**Pemilik (usulan):**

| Anggota | Fitur | Beban |
|---|---|---|
| 1 | F1 Cek Klarifikasi, F2 Pelacak Video | sedang |
| 2 | F4 Jaringan Koordinasi (simulator, graf, prediksi, GNN opsional) | berat |
| 3 | F3 Teknik Manipulasi, F5 Tindak Lanjut, kerangka dashboard, integrasi, Docker | sedang ke berat |

**Urutan prioritas jika waktu mepet:** F1, F2, F3, Kartu dahulu; kemudian F4 garis dasar dan F5; terakhir prediksi dan GNN. Kelima fitur sudah tertulis di proposal yang disubmit, jadi setiap fitur minimal harus berjalan pada kasus contoh walau versinya sederhana.

## 15. Definition of done (per fitur)

- Fungsi inti jalan dari antarmuka pada **kasus contoh** tanpa unggahan.
- Keluaran sesuai skema JSON dan membawa bukti serta keyakinan.
- Ada uji otomatis dan baris di `docs/EVALUASI.md`.
- Tidak melanggar batasan bagian 3.
- Mode offline: tetap berjalan dengan cache dan model lokal.
- Berjalan di Docker dengan satu perintah.

## 16. Pertanyaan terbuka (tanyakan ke tim, jangan menebak)

1. Model LLM dan penyedia mana yang dipakai, dan apakah ada anggaran API? (menentukan cadangan offline)
2. Streamlit saja, atau perlu React?
3. Tempat hosting demo publik yang dipakai?
4. Sumber klarifikasi publik mana yang boleh dikurasi, dan bagaimana lisensinya?
5. Apakah GNN dikerjakan, setelah inti selesai?
6. Apakah deskripsi karya di pendaftaran bisa diubah (tanya panitia)?

## 17. Glosarium

- **Daur ulang (video):** video lama yang dipakai ulang seolah kejadian terkini.
- **Koordinasi terindikasi:** pola perilaku akun yang sinkron dan mirip, sebuah indikasi, bukan vonis.
- **Seeder:** akun yang muncul paling awal pada sebuah kaskade/klaster.
- **Jembatan:** akun yang menghubungkan klaster terkoordinasi dengan komunitas organik.
- **Meteran konsensus:** perkiraan jumlah sumber independen di balik sebuah tren.
- **Prebunking:** pesan peringatan dini sebelum sebuah narasi menyebar luas.
- **Ablation:** membandingkan sistem dengan dan tanpa satu komponen untuk membuktikan manfaatnya.