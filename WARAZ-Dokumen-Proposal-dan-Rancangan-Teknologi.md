# WARAZ: Dokumen Proposal dan Rancangan Teknologi

*Kartika Cyber Hackathon 2026, Kategori 04 Siber Sosial | disusun 28 Oktober 2026*

**Tagline: WARAZ, Deteksi Koordinasi, Klarifikasi Narasi.**

**Cara membaca dokumen ini:** bagian Masalah, Solusi, dan lima Fitur Utama mengikuti proposal yang sudah disubmit. Dokumen ini menambahkan rancangan teknologi spesifik per fitur, data, evaluasi, pembagian kerja, dan roadmap. Nama pustaka disebut tanpa nomor versi, jadi cek kompatibilitasnya di hari pertama.

## 1. Ringkasan

WARAZ adalah lapisan analisis untuk satuan siber yang membantu memeriksa narasi yang beredar: apakah sudah pernah diklarifikasi, apakah videonya daur ulang, teknik manipulasi apa yang dipakai, bagaimana pola koordinasi penyebarannya, dan tindak lanjut apa yang bisa disiapkan. WARAZ **bukan pengumpul data mentah**. Data dimasukkan oleh pengguna atau analis, dalam bentuk teks, data agregat, atau data simulasi berlabel jelas.

## 2. Masalah

Maraknya penggunaan buzzer berbayar untuk menyebarkan informasi manipulatif di media sosial merusak ruang informasi, sementara konotasi buzzer telanjur dianggap negatif. Di sisi lain, satuan siber sering kesulitan menganalisis kerumitan narasi tersebut secara cepat karena keterbatasan alat analisis terpadu serta ketatnya regulasi privasi data.

## 3. Solusi

WARAZ hadir sebagai lapisan analisis (bukan pengumpul data mentah) yang membantu analis siber memproses data teks, agregat, maupun simulasi secara aman dan transparan. Sistem ini memvalidasi fakta, melacak jejak disinformasi, hingga memetakan dan menindaklanjuti jaringan buzzer tanpa melanggar privasi.

## 4. Kesesuaian dengan lomba

| Kriteria penilaian | Bobot | Cara WARAZ menjawabnya |
| --- | --- | --- |
| Relevansi dan manfaat bagi TNI AD | 25% | Alur kerja analis satuan: cek isu, telusuri, petakan, tindak lanjuti. Skenario demo bernuansa satuan (fiktif) |
| Inovasi teknis | 25% | Kombinasi pelacak daur ulang, peta teknik manipulasi, dan peta koordinasi dalam satu alur, dengan ablation yang jujur |
| Fungsionalitas purwarupa | 25% | Demo publik yang berjalan penuh pada kasus contoh, kelima fitur dapat dicoba juri |
| Kelayakan implementasi | 15% | Ringan, tanpa GPU, modular, dapat dijalankan offline lewat Docker |
| Kualitas dokumentasi | 10% | Dokumen ini, README, video demo, slide, catatan etika dan sumber data |

## 5. Fitur utama dan teknologinya

### 5.1 Cek Klarifikasi Isu

**Tujuan.** Memungkinkan pengguna atau analis memeriksa kebenaran serta status klarifikasi dari suatu isu yang beredar di ruang publik secara cepat dan valid.

**Cara kerja.**

1. Pengguna menempel teks isu atau tautan.
2. Sistem mengubah teks menjadi embedding, lalu mencari klaim paling mirip di **basis klarifikasi terkurasi** (pencarian kemiripan semantik, dengan pencarian kata kunci sebagai cadangan).
3. Sistem menampilkan status: *sudah diklarifikasi*, *ditemukan klaim mirip*, atau *belum ditemukan*, beserta ringkasan, tanggal, dan **tautan sumber klarifikasi**.
4. Model bahasa hanya dipakai untuk merangkum hasil yang ditemukan, **bukan untuk memberi vonis dari ingatannya sendiri**. Jika tidak ada sumber, sistem menyatakan tidak ada.

**Teknologi.**

| Komponen | Pilihan |
| --- | --- |
| Basis klarifikasi | SQLite: kolom klaim, status, ringkasan, tanggal, sumber, tautan |
| Pencarian semantik | sentence-transformers (model multibahasa), kemiripan cosine dengan NumPy (cukup untuk ratusan entri), atau FAISS bila membesar |
| Pencarian cadangan | rapidfuzz atau BM25 untuk kata kunci |
| Peringkasan terbatas | LLM lewat API dengan instruksi "hanya dari hasil" dan keluaran JSON tervalidasi Pydantic; model lokal lewat Ollama sebagai cadangan offline |

**Data.** Basis kurasi tim berisi 50-100 entri: skenario fiktif buatan tim, ditambah tautan dan ringkasan pendek dari sumber klarifikasi publik. Simpan ringkasan dan tautan, **bukan salinan artikel**. Cek lisensi sumber.

**Batasan jujur.** Frasa "valid" bergantung pada cakupan dan kualitas basis klarifikasi. Antarmuka harus menampilkan sumber dan tanggal, dan menyatakan bahwa *belum ditemukan* tidak berarti benar.

**Evaluasi.** Presisi dan recall pencocokan klaim pada set uji berisi parafrase dan klaim yang tidak ada di basis.

### 5.2 Pelacak Video Daur Ulang

**Tujuan.** Mendeteksi dan melacak penggunaan kembali video lama yang disebarkan di luar konteks aslinya, menggunakan arsip hash klip.

**Cara kerja.**

1. Ekstrak keyframe (misalnya 1 frame per 2 detik).
2. Hitung perceptual hash (pHash dan dHash) tiap frame.
3. Cocokkan dengan arsip memakai jarak Hamming. Kecocokan dinyatakan hanya bila **beberapa frame berurutan** cocok.
4. Tampilkan dua thumbnail berdampingan, skor, jumlah frame cocok, tanggal dan sumber asli.

**Teknologi.**

Komponen

Pilihan

Ekstraksi frame

ffmpeg, OpenCV

Hash

imagehash (pHash, dHash)

Arsip

SQLite: hash\_frame, urutan\_frame, judul, tanggal\_asli, sumber, tautan

Pencarian

Jarak Hamming dengan NumPy, atau BK-tree bila membesar

Pemeriksa kedua (opsional)

Embedding gambar (model gambar-teks) untuk video yang banyak diedit

**Data.** **Arsip demo dibuat sendiri:** tim merekam 10-30 klip fiktif (misalnya simulasi latihan), lalu membuat versi "daur ulang" dengan dipotong, dikompres, atau diberi teks. Ini menghindari masalah hak cipta dan konten sensitif, serta membuat kebenaran dasar diketahui. Simpan hash dan metadata, bukan salinan video.

**Batasan jujur.** Arsip kecil. Versi nyata membutuhkan kemitraan arsip media dan pemeriksa fakta. "Tidak ditemukan di arsip" tidak berarti video tersebut asli. Video yang dicerminkan atau diubah warnanya mungkin lolos, dan harus dicatat sebagai keterbatasan.

**Evaluasi.** Presisi dan recall pada klip asli, dipotong, dikompres, diberi teks, dan klip yang tidak ada di arsip.

### 5.3 Peta Teknik Manipulasi

**Tujuan.** Memetakan pola dan teknik psikologis atau rekayasa narasi, seperti urgensi palsu, framing ancaman, dan ilusi konsensus, yang digunakan dalam penyebaran informasi.

**Taksonomi awal:** framing ancaman, urgensi palsu, ilusi konsensus, pemicu amarah, kambing hitam atau us-vs-them, konteks dihapus atau dipotong, cherry-picking data, otoritas palsu, whataboutism.

**Cara kerja.**

1. Teks dikirim ke model bahasa dengan instruksi sistem berisi taksonomi, definisi, dan contoh (few-shot), termasuk contoh **bukan manipulasi**.
2. Keluaran berupa JSON terstruktur: teknik, skor, dan kutipan bukti.
3. Keluaran divalidasi Pydantic. Bila gagal, ulangi sekali, lalu tampilkan "tidak dapat dianalisis".
4. Dashboard menampilkan bar per teknik dan menyorot kutipan bukti pada teks asli.
5. Analis dapat mengatur ambang keyakinan dan mengabaikan label.

**Teknologi.**

Komponen

Pilihan

Klasifikasi utama

LLM lewat API dengan keluaran JSON terstruktur

Validasi

Pydantic

Cadangan offline

Model lokal lewat Ollama, atau klasifikator scikit-learn di atas embedding teks

Cache

File atau SQLite, agar demo cepat dan stabil

**Data dan evaluasi.** 100-200 postingan berlabel tangan oleh tim, dengan aturan pelabelan tertulis dan **kontra-contoh berupa kritik sah**. Ukur presisi, recall, dan F1 per teknik, lalu laporkan hasil termasuk kegagalan.

### 5.4 Pendeteksi dan Peta Koordinasi Jaringan

**Tujuan.** Mengidentifikasi dan menampilkan Peta Jaringan Koordinasi (kandidat sumber awal atau seeder, jembatan, dan akun organik), meteran konsensus, dan prediksi volume narasi, menggunakan data anonim atau simulasi berlabel jelas.

**Cara kerja.**

1. **Simulator** membuat jaringan akun anonim dengan kampanye terkoordinasi yang diketahui (kebenaran dasar), termasuk kampanye samar dan lonjakan organik yang menyerupai koordinasi.
2. **Graf temporal:** node adalah akun anonim, edge berstempel waktu (posting dalam jendela sempit, teks mirip, reply atau repost).
3. **Deteksi koordinasi (garis dasar):** sinkronisasi waktu, kemiripan teks (MinHash dan embedding), klastering komunitas.
4. **Peran akun:** seeder, jembatan, organik.
5. **Meteran konsensus:** jumlah klaster dan ukurannya diubah menjadi perkiraan sumber independen.
6. **Kandidat sumber awal:** rekonstruksi kaskade, skor dari waktu paling awal dan rumor centrality, keluaran berupa **peringkat dengan tingkat keyakinan**.
7. **Prediksi volume narasi (6-12 jam):** garis dasar ekstrapolasi eksponensial dibandingkan dengan proses Hawkes sederhana, tampil sebagai kurva dengan pita ketidakpastian.
8. **GNN (tahap lanjutan, opsional):** GraphSAGE atau GAT untuk klasifikasi akun dan peran. Dipertahankan **hanya jika ablation terhadap garis dasar menunjukkan manfaat**.

**Teknologi.**

Komponen

Pilihan

Simulator

NumPy, Pandas (atau Mesa)

Graf

NetworkX, python-igraph

Kemiripan teks

sentence-transformers, datasketch (MinHash)

Klastering

scikit-learn (DBSCAN, agglomerative), Louvain

Kandidat sumber awal

Implementasi sendiri di NetworkX

Prediksi

SciPy (proses Hawkes), garis dasar eksponensial

GNN (opsional)

PyTorch dan PyTorch Geometric, pelatihan di Colab atau Kaggle bila perlu

Visual

PyVis atau Cytoscape.js, Plotly

Penyimpanan

Parquet dengan DuckDB, atau SQLite

**Batasan jujur.**

- Evaluasi memakai data simulasi. Buzzer nyata jauh lebih beragam, sehingga validasi pada data nyata adalah langkah berikutnya bersama satuan.
- Hasil adalah **indikasi** koordinasi, bukan vonis. Koordinasi organik (komunitas yang bereaksi pada kejadian nyata) juga ada.
- "Kandidat sumber awal" bukan penentuan pelaku pasti.

**Evaluasi.** Presisi, recall, dan F1 deteksi koordinasi, akurasi top-1 dan top-3 sumber awal, MAE dan cakupan rentang prediksi, serta perbandingan garis dasar dengan GNN.

### 5.5 Mitigasi dan Tindak Lanjut

**Tujuan.** Mengirimkan daftar akun tertanda (flagged accounts) beserta bukti analisis pendukung agar dapat ditindaklanjuti secara langsung oleh pihak yang berwenang.

**Cara kerja.**

1. **Mesin rekomendasi berbasis aturan** menyarankan tindakan dari hasil Fitur 1-4. Contoh: risiko tinggi dan daur ulang terdeteksi, sarankan Kartu Klarifikasi dan eskalasi. Koordinasi terindikasi dengan keyakinan sedang, sarankan pemantauan lanjutan dan draf laporan.
2. **Daftar akun tertanda** disusun dari klaster terkoordinasi, berisi ID anonim, peran, skor, ciri klaster, dan bukti.
3. **Persetujuan analis:** setiap tindakan memerlukan persetujuan manusia sebelum paket dibuat.
4. **Paket bukti** diekspor (PDF dan JSON) untuk diserahkan kepada pihak berwenang melalui kanal resmi. WARAZ tidak melapor atau bertindak otomatis ke platform maupun akun.
5. **Kartu Klarifikasi** (PNG) dan draf pesan peringatan dini (prebunking) disiapkan sebagai opsi tindak lanjut.
6. **Jejak audit** mencatat saran sistem, keputusan analis, dan waktu.

**Teknologi.**

Komponen

Pilihan

Aturan rekomendasi

Berkas YAML atau JSON berisi aturan, dievaluasi dengan Python

Tiket kasus

SQLite

Paket bukti

ReportLab atau WeasyPrint untuk PDF, JSON untuk mesin

Kartu Klarifikasi

Pillow

Jejak audit

JSONL

Alur persetujuan

Peran sederhana (pengguna dan analis) di Streamlit atau React

**Penting tentang "akun tertanda".** Pada demo, semua akun adalah **ID anonim atau simulasi berlabel jelas**. Rulebook melarang data pribadi pihak ketiga tanpa izin yang sah. Pada penerapan nyata, pengaitan ID dengan identitas hanya dilakukan oleh pihak berwenang melalui proses hukum mereka sendiri, di luar WARAZ. Daftar bersifat "tertanda berdasarkan indikasi", bukan daftar pelaku.

## 6. Arsitektur sistem

\[Pengguna / Analis]\
|\
\[Antarmuka web: Cek Cepat, Dashboard, Tinjau dan Koreksi]\
|\
\[Lapisan layanan (FastAPI atau langsung Streamlit)]\
|\
+----------+----------+-----------+-------------+\
| F1       | F2       | F3        | F4          |\
| Cek      | Video    | Teknik    | Jaringan    |\
| klarif.  | daur     | manipulasi| koordinasi, |\
|          | ulang    |           | prediksi    |\
+----------+----------+-----------+-------------+\
|\
\[F5: aturan rekomendasi, tiket, paket bukti, Kartu]\
|\
\[Persetujuan analis]  -->  \[Jejak audit JSONL]\
|\
\[Penyimpanan: SQLite / Parquet]

## 7. Tabel stack ringkas

Lapisan

Teknologi

Bahasa

Python

Video

ffmpeg, OpenCV, imagehash

Teks dan semantik

sentence-transformers, rapidfuzz atau BM25, LLM API, Pydantic, Ollama (cadangan)

Klasifikasi

scikit-learn

Graf dan koordinasi

NetworkX, python-igraph, datasketch, SciPy

GNN (opsional)

PyTorch, PyTorch Geometric

Data

SQLite, Parquet, DuckDB, simulator buatan sendiri

Antarmuka

Streamlit (cepat) atau React, Plotly, PyVis

Dokumen dan gambar

Pillow, ReportLab atau WeasyPrint

Pengemasan

Docker, plus hosting publik untuk juri

**Prinsip rekayasa:** satu repositori, satu perintah untuk menjalankan, cache hasil model agar demo stabil, **tidak ada kunci API berbayar di demo publik**, dan mode offline lewat Docker untuk poin kelayakan implementasi.

## 8. Data dan keterbatasannya

- WARAZ tidak mengambil data sendiri dari media sosial. Analis atau pengguna yang memasukkan data.
- **Untuk lomba:** basis klarifikasi kurasi tim, arsip video demo buatan sendiri, teks tulisan tim, dan simulator jaringan dengan kebenaran dasar. Semua berlabel **DATA SIMULASI**.
- **Untuk penerapan nyata:** ekspor dari alat pemantau yang sudah dipakai satuan atau penyedia data berlisensi, dalam bentuk anonim atau agregat.
- Format CSV yang didukung: akun\_id (anonim), waktu, teks, tipe, induk\_id.
- Sampaikan terang-terangan di presentasi bahwa validasi pada data nyata adalah langkah berikutnya.

## 9. Etika dan guardrail

1. **Manusia memutuskan.** Sistem menyarankan, analis menyetujui, tidak ada tindakan otomatis.
2. **Jejak audit** untuk setiap label dan keputusan.
3. **Anonim dan agregat.** Tidak ada identitas dunia nyata di dalam sistem.
4. **Bahasa netral:** "indikasi amplifikasi terkoordinasi" dan "akun tertanda berdasarkan indikasi", bukan vonis "buzzer" atau "pelaku".
5. **Kritik sah dilindungi** lewat kontra-contoh di set uji dan ambang keyakinan yang bisa diatur.
6. **Tidak ada akun penyamaran** atau buzzer tandingan.
7. **Klaim privasi harus benar:** berkas unggahan hanya boleh dinyatakan tidak disimpan bila aplikasi benar-benar menghapusnya setelah diproses.
8. **Keterbukaan:** jenis data, lisensi sumber, dan keterbatasan dicatat di dokumentasi.

## 10. Pembagian kerja (usulan, tim 3 orang)

Fitur dibagi berdasarkan kemiripan teknologi dan beban kerja. Sesuaikan dengan keahlian masing-masing.

Anggota

Fitur

Teknologi utama

Beban

**Anggota 1: Pencocokan dan konten**

F1 Cek Klarifikasi Isu, F2 Pelacak Video Daur Ulang

sentence-transformers, SQLite, ffmpeg, OpenCV, imagehash

Sedang

**Anggota 2: Jaringan dan analitik**

F4 Pendeteksi dan Peta Koordinasi Jaringan (simulator, graf, prediksi, GNN opsional)

NetworkX, scikit-learn, datasketch, SciPy, PyG, PyVis

**Berat**

**Anggota 3: Teknik, tindak lanjut, dan antarmuka**

F3 Peta Teknik Manipulasi, F5 Mitigasi dan Tindak Lanjut, kerangka dashboard, integrasi

LLM API, Pydantic, Pillow, ReportLab, Streamlit atau React, Docker

Sedang ke berat

**Catatan beban:** Anggota 2 memegang bagian paling berat. Jika perlu, pindahkan simulator ke Anggota 1 (bekerja sama dengan pengarsipan data) atau pindahkan kerangka dashboard ke Anggota 1. Ketua tim sebaiknya juga memegang dokumen, video, slide, dan koordinasi.

**Tanggung jawab bersama:** set evaluasi dan label, README, atribusi komponen pihak ketiga, dan latihan presentasi.

## 11. Roadmap (28 Oktober sampai 15 November 2026)

Tanggal

Fokus

Hasil

28-29 Okt

Kunci cakupan dan pembagian, siapkan repositori, uji instalasi (terutama PyTorch Geometric dan ffmpeg), putuskan hosting demo, tanyakan ke panitia soal perubahan deskripsi karya

Repositori jalan, tiap orang bisa menjalankan README

30 Okt - 3 Nov

Data: basis klarifikasi, arsip video demo, simulator, set label. Mulai tiap fitur

Data siap, versi pertama F1, F2, F3, F4 (garis dasar)

4-5 Nov

Integrasi alur utama. **Ikut webinar 5 November**, tanyakan harapan juri

Alur Cek Cepat sampai Kartu berjalan

6-9 Nov

F4 lengkap (peta peran, prediksi), F5 (aturan, paket bukti, persetujuan), dashboard, deploy demo publik, GNN bila inti stabil

Kelima fitur dapat dicoba di demo publik

10-12 Nov

Tabel evaluasi jujur, uji dari perangkat dan jaringan lain, README, screenshot (maks 5), thumbnail 1200x630

Dokumentasi lengkap

13 Nov

**Bekukan fitur.** Rekam video (maks 10 menit, unggah ke YouTube), finalisasi slide

Video dan slide siap

14 Nov

**Kumpulkan** di platform

Submission masuk

16 / 20 / 24 Nov

Penjurian online / pengumuman finalis / final di Jakarta (presentasi 10 menit)

**Prioritas jika waktu mepet:** F1, F2, F3, dan Kartu dahulu; kemudian F4 garis dasar dan F5; terakhir prediksi dan GNN. Karena kelima fitur sudah tertulis di proposal, pastikan masing-masing minimal berjalan pada kasus contoh, walau versinya sederhana.

## 12. Evaluasi

Fitur

Metrik

Cara uji

F1

Presisi dan recall pencocokan klaim

Set uji parafrase dan klaim di luar basis

F2

Presisi dan recall pencocokan

Klip asli, dipotong, dikompres, diberi teks, dan di luar arsip

F3

Presisi, recall, F1 per teknik

100-200 contoh berlabel, termasuk kritik sah

F4

F1 koordinasi, top-1 dan top-3 sumber awal, MAE prediksi, garis dasar vs GNN

Data simulasi dengan kebenaran dasar

F5

Kelayakan alur dan kelengkapan paket

Uji coba alur dengan anggota tim sebagai analis

Sistem

Waktu dari input sampai Kartu jadi

Stopwatch

Tampilkan **satu tabel hasil jujur**, termasuk kasus gagal dan penyebabnya.

## 13. Rencana demo dan kelengkapan submission

**Alur demo 3-5 menit:**

1. Cek isu: tempel klaim, lihat status klarifikasi dan sumber.
2. Unggah video: kecocokan arsip, dua thumbnail berdampingan.
3. Peta teknik manipulasi pada teks yang menyertai video.
4. Peta jaringan koordinasi, meteran konsensus, kandidat sumber awal, kurva prediksi.
5. Mitigasi: rekomendasi, persetujuan analis, paket bukti, Kartu Klarifikasi.

**Kelengkapan yang diwajibkan rulebook:**

- ☐ Link karya publik yang bisa dicoba juri tanpa instalasi
- ☐ Thumbnail 1200x630 px, JPG/PNG/WebP, maksimal 500KB
- ☐ Screenshot, maksimal 5 gambar
- ☐ Video maksimal 10 menit di YouTube
- ☐ Slide penjelasan (fitur, arsitektur, teknologi)
- ☐ Deklarasi komponen pre-existing dan atribusi pustaka pihak ketiga

Siapkan **video rekaman cadangan** dan data demo tertanam supaya demo tidak gagal karena koneksi.

## 14. Risiko dan penanganannya

Risiko

Penanganan

Lima fitur terlalu banyak untuk 3 orang dan 18 hari

Kunci versi minimum per fitur, fokus pada alur terpadu, bekukan fitur 13 November

Basis klarifikasi kecil atau dipertanyakan

Tampilkan sumber dan tanggal, jujur soal cakupan, roadmap kemitraan

Arsip video kecil

Arsip demo buatan sendiri, jujur soal skala

LLM tidak konsisten atau API gagal

Validasi Pydantic, cache, model lokal cadangan, video cadangan

GNN tidak lebih baik dari garis dasar

Laporkan jujur dan pertahankan garis dasar

"Akun tertanda" dipersepsikan sebagai pengawasan

Anonim, indikasi bukan vonis, persetujuan manusia, tanpa tindakan otomatis

Data sintetis dianggap terlalu mudah

Skenario samar dan lonjakan organik

Pemasangan pustaka bermasalah

Uji di hari pertama, siapkan Docker dan Colab

## 15. Kelayakan penerapan dan pengembangan lanjutan

- **Di satuan:** berjalan di laptop biasa tanpa GPU, dapat dipaketkan dengan Docker, dan dapat dioperasikan offline dengan model lokal sebagai cadangan.
- **Tahap berikutnya:** perluas basis klarifikasi dan arsip video lewat kemitraan, uji pada data nyata anonim bersama satuan, dukungan bahasa daerah, peningkatan prediksi, dan integrasi dengan alat pemantau yang sudah dipakai.
- **Hak kekayaan intelektual** tetap milik tim. Rulebook memberi PUSSIBERAD hak mengadopsi ide teknis dengan diskusi bersama tim, yang dapat diposisikan sebagai peluang kolaborasi.

## 16. Rujukan

- Rulebook Kartika Cyber Hackathon 2026 (PUSSIBERAD dan CODEPOLITAN, Oktober 2026)
- Dokumen internal tim: Deskripsi WARAZ, Masalah, Solusi, Fitur

| Komponen | Pilihan |
| --- | --- |
| Ekstraksi frame | ffmpeg, OpenCV |
| Hash | imagehash (pHash, dHash) |
| Arsip | SQLite: hash_frame, urutan_frame, judul, tanggal_asli, sumber, tautan |
| Pencarian | Jarak Hamming dengan NumPy, atau BK-tree bila membesar |
| Pemeriksa kedua (opsional) | Embedding gambar (model gambar-teks) untuk video yang banyak diedit |

| Komponen | Pilihan |
| --- | --- |
| Klasifikasi utama | LLM lewat API dengan keluaran JSON terstruktur |
| Validasi | Pydantic |
| Cadangan offline | Model lokal lewat Ollama, atau klasifikator scikit-learn di atas embedding teks |
| Cache | File atau SQLite, agar demo cepat dan stabil |

| Komponen | Pilihan |
| --- | --- |
| Simulator | NumPy, Pandas (atau Mesa) |
| Graf | NetworkX, python-igraph |
| Kemiripan teks | sentence-transformers, datasketch (MinHash) |
| Klastering | scikit-learn (DBSCAN, agglomerative), Louvain |
| Kandidat sumber awal | Implementasi sendiri di NetworkX |
| Prediksi | SciPy (proses Hawkes), garis dasar eksponensial |
| GNN (opsional) | PyTorch dan PyTorch Geometric, pelatihan di Colab atau Kaggle bila perlu |
| Visual | PyVis atau Cytoscape.js, Plotly |
| Penyimpanan | Parquet dengan DuckDB, atau SQLite |

| Komponen | Pilihan |
| --- | --- |
| Aturan rekomendasi | Berkas YAML atau JSON berisi aturan, dievaluasi dengan Python |
| Tiket kasus | SQLite |
| Paket bukti | ReportLab atau WeasyPrint untuk PDF, JSON untuk mesin |
| Kartu Klarifikasi | Pillow |
| Jejak audit | JSONL |
| Alur persetujuan | Peran sederhana (pengguna dan analis) di Streamlit atau React |

| Lapisan | Teknologi |
| --- | --- |
| Bahasa | Python |
| Video | ffmpeg, OpenCV, imagehash |
| Teks dan semantik | sentence-transformers, rapidfuzz atau BM25, LLM API, Pydantic, Ollama (cadangan) |
| Klasifikasi | scikit-learn |
| Graf dan koordinasi | NetworkX, python-igraph, datasketch, SciPy |
| GNN (opsional) | PyTorch, PyTorch Geometric |
| Data | SQLite, Parquet, DuckDB, simulator buatan sendiri |
| Antarmuka | Streamlit (cepat) atau React, Plotly, PyVis |
| Dokumen dan gambar | Pillow, ReportLab atau WeasyPrint |
| Pengemasan | Docker, plus hosting publik untuk juri |

| Anggota | Fitur | Teknologi utama | Beban |
| --- | --- | --- | --- |
| Anggota 1: Pencocokan dan konten | F1 Cek Klarifikasi Isu, F2 Pelacak Video Daur Ulang | sentence-transformers, SQLite, ffmpeg, OpenCV, imagehash | Sedang |
| Anggota 2: Jaringan dan analitik | F4 Pendeteksi dan Peta Koordinasi Jaringan (simulator, graf, prediksi, GNN opsional) | NetworkX, scikit-learn, datasketch, SciPy, PyG, PyVis | Berat |
| Anggota 3: Teknik, tindak lanjut, dan antarmuka | F3 Peta Teknik Manipulasi, F5 Mitigasi dan Tindak Lanjut, kerangka dashboard, integrasi | LLM API, Pydantic, Pillow, ReportLab, Streamlit atau React, Docker | Sedang ke berat |

| Tanggal | Fokus | Hasil |
| --- | --- | --- |
| 28-29 Okt | Kunci cakupan dan pembagian, siapkan repositori, uji instalasi (terutama PyTorch Geometric dan ffmpeg), putuskan hosting demo, tanyakan ke panitia soal perubahan deskripsi karya | Repositori jalan, tiap orang bisa menjalankan README |
| 30 Okt - 3 Nov | Data: basis klarifikasi, arsip video demo, simulator, set label. Mulai tiap fitur | Data siap, versi pertama F1, F2, F3, F4 (garis dasar) |
| 4-5 Nov | Integrasi alur utama. Ikut webinar 5 November, tanyakan harapan juri | Alur Cek Cepat sampai Kartu berjalan |
| 6-9 Nov | F4 lengkap (peta peran, prediksi), F5 (aturan, paket bukti, persetujuan), dashboard, deploy demo publik, GNN bila inti stabil | Kelima fitur dapat dicoba di demo publik |
| 10-12 Nov | Tabel evaluasi jujur, uji dari perangkat dan jaringan lain, README, screenshot (maks 5), thumbnail 1200x630 | Dokumentasi lengkap |
| 13 Nov | Bekukan fitur. Rekam video (maks 10 menit, unggah ke YouTube), finalisasi slide | Video dan slide siap |
| 14 Nov | Kumpulkan di platform | Submission masuk |
| 16 / 20 / 24 Nov | Penjurian online / pengumuman finalis / final di Jakarta (presentasi 10 menit) |  |

| Fitur | Metrik | Cara uji |
| --- | --- | --- |
| F1 | Presisi dan recall pencocokan klaim | Set uji parafrase dan klaim di luar basis |
| F2 | Presisi dan recall pencocokan | Klip asli, dipotong, dikompres, diberi teks, dan di luar arsip |
| F3 | Presisi, recall, F1 per teknik | 100-200 contoh berlabel, termasuk kritik sah |
| F4 | F1 koordinasi, top-1 dan top-3 sumber awal, MAE prediksi, garis dasar vs GNN | Data simulasi dengan kebenaran dasar |
| F5 | Kelayakan alur dan kelengkapan paket | Uji coba alur dengan anggota tim sebagai analis |
| Sistem | Waktu dari input sampai Kartu jadi | Stopwatch |

| Risiko | Penanganan |
| --- | --- |
| Lima fitur terlalu banyak untuk 3 orang dan 18 hari | Kunci versi minimum per fitur, fokus pada alur terpadu, bekukan fitur 13 November |
| Basis klarifikasi kecil atau dipertanyakan | Tampilkan sumber dan tanggal, jujur soal cakupan, roadmap kemitraan |
| Arsip video kecil | Arsip demo buatan sendiri, jujur soal skala |
| LLM tidak konsisten atau API gagal | Validasi Pydantic, cache, model lokal cadangan, video cadangan |
| GNN tidak lebih baik dari garis dasar | Laporkan jujur dan pertahankan garis dasar |
| "Akun tertanda" dipersepsikan sebagai pengawasan | Anonim, indikasi bukan vonis, persetujuan manusia, tanpa tindakan otomatis |
| Data sintetis dianggap terlalu mudah | Skenario samar dan lonjakan organik |
| Pemasangan pustaka bermasalah | Uji di hari pertama, siapkan Docker dan Colab |