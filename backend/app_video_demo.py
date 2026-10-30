"""Aplikasi Antarmuka Demo Streamlit untuk Fitur 2: Pelacak Video Daur Ulang.

Dapat dijalankan langsung dengan perintah:
    streamlit run backend/app_video_demo.py
"""

import os
import shutil
import sys
import uuid
from pathlib import Path

import streamlit as st
from PIL import Image

# Pastikan modul backend dapat diimpor
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.db.koneksi import SessionLocal, init_db
from src.db.skema import ArsipVideo, HashFrame
from src.video.konfigurasi import STATUS_DAUR_ULANG, TEMP_DIR, THUMBNAIL_DIR
from src.video.layanan import (
    daftarkan_video_arsip,
    dapatkan_daftar_arsip,
    deteksi_video_daur_ulang,
)
from src.video.skrip_demo import DEMO_DIR, seed_arsip_demo, siapkan_koleksi_demo

st.set_page_config(
    page_title="WARAZ — Pelacak Video Daur Ulang",
    page_icon="🛡️",
    layout="wide",
)

# Inisialisasi Database pada startup
init_db()


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass


def hapus_berkas_aman(path: Path):
    """Menghapus berkas sementara secara aman di Windows tanpa crash."""
    if path and path.exists():
        try:
            path.unlink()
        except Exception:
            pass


st.title("🛡️ WARAZ — Pelacak Video Daur Ulang (F2)")
st.caption("Deteksi penggunaan kembali video lama yang disebarkan di luar konteks aslinya menggunakan arsip perceptual hash.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Pengaturan Lingkungan")

    # Mode Operasi: Demo vs Production
    mode_lingkungan = st.radio(
        "Mode Sistem:",
        ["Mode Demo (Lomba & Evaluasi)", "Mode Produksi (Operasional Riil)"],
        index=0,
        help="Pada Mode Produksi, klip uji sintetis disembunyikan dan sistem siap menerima input riil.",
    )
    is_mode_demo = "Demo" in mode_lingkungan

    if is_mode_demo:
        st.info("🏷️ **DATA SIMULASI AKTIF**\nArsip menggunakan klip sintetis lokal tanpa hak cipta.")
    else:
        st.success("🏢 **MODE PRODUKSI AKTIF**\nSiap terintegrasi dengan arsip media & platform siber.")

    db = get_db()

    if is_mode_demo:
        st.divider()
        st.subheader("🛠️ Manajemen Arsip Demo")
        if st.button("🚀 Inisialisasi / Seed Arsip Demo", use_container_width=True):
            with st.spinner("Menyiapkan video demo sintetis dan menghitung hash..."):
                seed_arsip_demo(db)
            st.success("Basis video demo berhasil disiapkan!")

    st.divider()
    st.subheader("📚 Arsip Video Tersimpan")
    daftar_arsip = dapatkan_daftar_arsip(db)
    st.write(f"Total video di arsip: **{len(daftar_arsip)}**")
    for a in daftar_arsip:
        with st.expander(f"📁 {a['judul'][:26]}..."):
            st.write(f"**Tanggal:** {a.get('tanggal_asli') or '-'}")
            st.write(f"**Sumber:** {a.get('sumber') or '-'}")
            st.write(f"**Frame hash:** {a['total_frame']} frame")
            if a.get("thumbnail_filename"):
                t_path = THUMBNAIL_DIR / a["thumbnail_filename"]
                if t_path.exists():
                    st.image(str(t_path), use_container_width=True)

tab_analisis, tab_arsip_baru = st.tabs(["🔍 Analisis Video Uji", "➕ Daftarkan Video Baru ke Arsip"])

# ─────────────────────────────────────────────────────────────
# TAB 1: Analisis Video Uji
# ─────────────────────────────────────────────────────────────
with tab_analisis:
    video_siap_uji = None
    nama_video_uji = ""

    analisis_key = st.session_state.get("analisis_key", 0)

    if is_mode_demo:
        col_input, col_preset = st.columns([1, 1])

        with col_input:
            st.subheader("1. Unggah Berkas Video")
            uploaded_file = st.file_uploader(
                "Pilih berkas video (MP4, MKV, WebM):",
                type=["mp4", "mkv", "webm", "avi"],
                key=f"uploader_analisis_{analisis_key}",
            )
            if uploaded_file is not None:
                ext = Path(uploaded_file.name).suffix or ".mp4"
                temp_path = TEMP_DIR / f"upload_ui_{uuid.uuid4()}{ext}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                video_siap_uji = temp_path
                nama_video_uji = uploaded_file.name

        with col_preset:
            st.subheader("Atau Pilih Klip Uji Demo")
            koleksi = siapkan_koleksi_demo()
            pilihan = st.radio(
                "Skenario uji manipulasi:",
                [
                    "Klip Daur Ulang: Potongan Durasi (Detik 2-6 dari Simulasi Gempa)",
                    "Klip Daur Ulang: Ditambahi Banner Hoaks (Apel Siaga Kodam)",
                    "Klip Non-Arsip: Video Baru Orisinal (Festival Budaya)",
                ],
                index=0,
                key=f"preset_radio_{analisis_key}",
            )

            if st.button("Gunakan Klip Skenario Ini", use_container_width=True):
                if "Potongan" in pilihan:
                    video_siap_uji = koleksi["uji_cut"]
                    nama_video_uji = "uji_daur_ulang_potongan.mp4"
                elif "Banner" in pilihan:
                    video_siap_uji = koleksi["uji_teks"]
                    nama_video_uji = "uji_daur_ulang_banner_palsu.mp4"
                else:
                    video_siap_uji = koleksi["uji_baru"]
                    nama_video_uji = "uji_video_orisinal_baru.mp4"
                st.session_state["preset_video"] = str(video_siap_uji)
                st.session_state["preset_name"] = nama_video_uji

        if "preset_video" in st.session_state and video_siap_uji is None:
            video_siap_uji = Path(st.session_state["preset_video"])
            nama_video_uji = st.session_state["preset_name"]

    else:
        # MODE PRODUKSI: Tampilan bersih tanpa klip buatan sendiri
        st.subheader("Analisis Verifikasi Keaslian Video")
        col_upload, col_url = st.columns([1, 1])

        with col_upload:
            st.markdown("##### Opsi A: Unggah Berkas Video")
            uploaded_file = st.file_uploader(
                "Berkas video bukti (MP4, MKV, WebM):",
                type=["mp4", "mkv", "webm", "avi"],
                key=f"uploader_prod_{analisis_key}",
            )
            if uploaded_file is not None:
                ext = Path(uploaded_file.name).suffix or ".mp4"
                temp_path = TEMP_DIR / f"upload_prod_{uuid.uuid4()}{ext}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                video_siap_uji = temp_path
                nama_video_uji = uploaded_file.name

        with col_url:
            st.markdown("##### Opsi B: Tautan Video Media Sosial (Roadmap Integrasi)")
            st.text_input(
                "URL Video (TikTok / X / Reels / YouTube Shorts):",
                placeholder="https://www.tiktok.com/@user/video/...",
                disabled=True,
                help="Fitur ekstraksi streaming URL platform dijadwalkan pada roadmap implementasi tahap produksi.",
            )
            st.caption("ℹ️ *Pada deployment produksi satuan, input URL diunduh sementara via streaming collector aman.*")

    st.divider()

    # Tampilkan tombol periksa dan tombol reset
    if video_siap_uji and video_siap_uji.exists():
        c_status, c_reset = st.columns([3, 1])
        with c_status:
            st.success(f"Video terpilih untuk dianalisis: **{nama_video_uji}**")
        with c_reset:
            if st.button("🔄 Bersihkan / Ganti Video", use_container_width=True):
                if "preset_video" in st.session_state:
                    del st.session_state["preset_video"]
                if "preset_name" in st.session_state:
                    del st.session_state["preset_name"]
                st.session_state["analisis_key"] = analisis_key + 1
                st.rerun()

        if st.button("⚡ Jalankan Pelacak Daur Ulang", type="primary", use_container_width=True):
            with st.spinner("Mengekstrak keyframe, menghitung pHash & dHash, mencocokkan sequence..."):
                hasil = deteksi_video_daur_ulang(db=db, video_path=video_siap_uji)

            st.subheader("📊 Hasil Deteksi")

            # Metrik utama
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                is_recycled = hasil["status"] == STATUS_DAUR_ULANG
                if is_recycled:
                    st.error("🚨 KEMUNGKINAN DAUR ULANG")
                else:
                    st.success("✅ TIDAK DITEMUKAN DI ARSIP")
            with m2:
                st.metric("Skor Kemiripan", f"{hasil['skor'] * 100:.1f}%")
            with m3:
                st.metric("Tingkat Keyakinan", hasil["keyakinan"].upper())
            with m4:
                st.metric("Frame Cocok / Total", f"{hasil['frame_cocok']} / {hasil['frame_total']}")

            st.write(f"ℹ️ **Keterangan:** {hasil['catatan']}")

            # Visualisasi Komparasi Berdampingan
            st.subheader("🖼️ Komparasi Visual Berdampingan (Side-by-Side)")
            c_left, c_right = st.columns(2)

            with c_left:
                st.markdown("#### Video yang Diperiksa (Input)")
                q_thumb = TEMP_DIR / hasil.get("query_thumbnail_filename", "")
                if q_thumb.exists():
                    st.image(str(q_thumb), caption="Thumbnail Video Input", use_container_width=True)
                else:
                    st.info("Thumbnail video input tidak tersedia.")

            with c_right:
                st.markdown("#### Video Acuan Asli di Arsip")
                if is_recycled and hasil.get("arsip_tercocok"):
                    arsip_info = hasil["arsip_tercocok"]
                    t_filename = arsip_info.get("thumbnail_filename")
                    a_thumb = THUMBNAIL_DIR / t_filename if t_filename else None
                    if a_thumb and a_thumb.exists():
                        st.image(str(a_thumb), caption=f"Arsip: {arsip_info['judul']}", use_container_width=True)

                    st.markdown(f"""
                    - **Judul Asli:** {arsip_info.get('judul')}
                    - **Tanggal Peristiwa Asli:** `{arsip_info.get('tanggal_asli') or 'Tidak diketahui'}`
                    - **Penerbit/Sumber Resmi:** `{arsip_info.get('sumber') or '-'}`
                    - **Tautan Klarifikasi:** [{arsip_info.get('tautan')}]({arsip_info.get('tautan')})
                    """)
                else:
                    st.info("Tidak ada klip arsip yang berurutan cocok.")

            # Rincian Teknis Analisis
            with st.expander("🔬 Rincian Teknis & Parameter"):
                st.json({
                    "consecutive_run": hasil.get("consecutive_run"),
                    "avg_hamming": hasil.get("avg_hamming"),
                    "frame_cocok": hasil.get("frame_cocok"),
                    "frame_total": hasil.get("frame_total"),
                    "info_video": hasil.get("info_video"),
                    "detail_pasangan": hasil.get("detail_pasangan"),
                })

            st.divider()
            st.caption(
                "⚖️ **Guardrail & Batasan Etika:** 'Tidak ditemukan di arsip' tidak otomatis berarti video baru "
                "(tergantung kelengkapan arsip). Keputusan akhir diserahkan kepada analis manusia (human-in-the-loop)."
            )

# ─────────────────────────────────────────────────────────────
# TAB 2: Pendaftaran Arsip Baru (Anti-Duplikat & Auto-Reset)
# ─────────────────────────────────────────────────────────────
with tab_arsip_baru:
    st.subheader("Tambah Klip Video ke Basis Arsip")
    st.write("Daftarkan video dokumentasi asli agar sistem dapat mendeteksi daur ulang di masa depan.")

    # Tampilkan notifikasi sukses jika baru saja berhasil mendaftar
    if "pesan_sukses_arsip" in st.session_state:
        st.success(st.session_state.pop("pesan_sukses_arsip"))

    form_version = st.session_state.get("form_version", 0)

    # Menggunakan key dinamis agar form otomatis ter-reset bersih setelah submit
    with st.form(f"form_arsip_{form_version}", clear_on_submit=True):
        f_upload = st.file_uploader(
            "Berkas Video Asli:",
            type=["mp4", "mkv", "webm", "avi"],
            key=f"file_uploader_arsip_{form_version}",
        )
        f_judul = st.text_input(
            "Judul / Deskripsi Peristiwa:",
            placeholder="Misal: Latihan Penanggulangan Banjir BPBD 2024",
            key=f"judul_arsip_{form_version}",
        )
        f_tanggal = st.date_input("Tanggal Asli Kejadian:", key=f"tgl_arsip_{form_version}")
        f_sumber = st.text_input(
            "Sumber Resmi / Kanal Publikasi:",
            placeholder="Misal: Humas BNPB / YouTube Resmi",
            key=f"sumber_arsip_{form_version}",
        )
        f_tautan = st.text_input(
            "Tautan / Link Berita Asli:",
            placeholder="https://bnpb.go.id/...",
            key=f"link_arsip_{form_version}",
        )
        btn_submit = st.form_submit_button("💾 Simpan ke Basis Arsip", use_container_width=True)

        if btn_submit:
            judul_bersih = f_judul.strip() if f_judul else ""

            # 1. Validasi kelengkapan form
            if not f_upload or not judul_bersih:
                st.error("⚠️ Berkas video dan judul wajib diisi.")
            else:
                # 2. Cek apakah judul video sudah ada di database (Cegah Duplikat)
                duplikat = db.query(ArsipVideo).filter(ArsipVideo.judul.ilike(judul_bersih)).first()
                if duplikat:
                    st.warning(
                        f"⚠️ Video dengan judul **'{judul_bersih}'** sudah pernah terdaftar di arsip (ID: `{duplikat.id}`). "
                        "Silakan gunakan judul berbeda untuk mencegah duplikasi data."
                    )
                else:
                    with st.spinner("Mengekstrak keyframe dan menyimpan perceptual hash ke database..."):
                        ext = Path(f_upload.name).suffix or ".mp4"
                        t_raw_path = TEMP_DIR / f"arsip_ui_{uuid.uuid4()}{ext}"
                        with open(t_raw_path, "wb") as f:
                            f.write(f_upload.getbuffer())

                        try:
                            info_baru = daftarkan_video_arsip(
                                db=db,
                                video_path=t_raw_path,
                                judul=judul_bersih,
                                tanggal_asli=str(f_tanggal),
                                sumber=f_sumber.strip() if f_sumber else None,
                                tautan=f_tautan.strip() if f_tautan else None,
                            )
                            # Simpan pesan sukses dan reset form ke awal secara instan
                            st.session_state["form_version"] = form_version + 1
                            st.session_state["pesan_sukses_arsip"] = (
                                f"🎉 Berhasil! Video **'{judul_bersih}'** telah didaftarkan ke arsip "
                                f"dengan {info_baru['total_frame_hash']} keyframe hash."
                            )
                            st.rerun()

                        except Exception as e:
                            st.error(f"Gagal mendaftarkan video: {str(e)}")
                        finally:
                            hapus_berkas_aman(t_raw_path)
