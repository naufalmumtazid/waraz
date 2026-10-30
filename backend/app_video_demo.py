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
    """Menghapus berkas sementara secara aman di Windows tanpa crash jika handle terkunci sesaat."""
    if path and path.exists():
        try:
            path.unlink()
        except Exception:
            pass


st.title("🛡️ WARAZ — Pelacak Video Daur Ulang (F2)")
st.caption("Deteksi penggunaan kembali video lama yang disebarkan di luar konteks aslinya menggunakan arsip perceptual hash.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Pengaturan & Arsip Demo")
    st.info("Label: **DATA SIMULASI**\nSemua video dibuat secara lokal tanpa melanggar hak cipta.")

    db = get_db()
    if st.button("🚀 Inisialisasi / Seed Arsip Demo", use_container_width=True):
        with st.spinner("Menyiapkan video demo sintetis dan menghitung hash..."):
            seed_arsip_demo(db)
        st.success("Basis video demo berhasil disiapkan!")

    st.divider()
    st.subheader("📚 Arsip Video Tersimpan")
    daftar_arsip = dapatkan_daftar_arsip(db)
    st.write(f"Total video di arsip: **{len(daftar_arsip)}**")
    for a in daftar_arsip:
        with st.expander(f"📁 {a['judul'][:28]}..."):
            st.write(f"**Tanggal:** {a.get('tanggal_asli') or '-'}")
            st.write(f"**Sumber:** {a.get('sumber') or '-'}")
            st.write(f"**Frame hash:** {a['total_frame']} frame")
            if a.get("thumbnail_filename"):
                t_path = THUMBNAIL_DIR / a["thumbnail_filename"]
                if t_path.exists():
                    st.image(str(t_path), use_container_width=True)

tab_analisis, tab_arsip_baru = st.tabs(["🔍 Analisis Video Uji", "➕ Daftarkan Video Baru ke Arsip"])

with tab_analisis:
    col_input, col_preset = st.columns([1, 1])

    video_siap_uji = None
    nama_video_uji = ""

    with col_input:
        st.subheader("1. Unggah Berkas Video")
        uploaded_file = st.file_uploader(
            "Pilih berkas video (MP4, MKV, WebM):",
            type=["mp4", "mkv", "webm", "avi"],
            key="video_uploader",
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
            "Skenario uji:",
            [
                "Klip Daur Ulang: Potongan Durasi (Detik 2-6 dari Simulasi Gempa)",
                "Klip Daur Ulang: Ditambahi Banner Hoaks (Apel Siaga Kodam)",
                "Klip Non-Arsip: Video Baru Orisinal (Festival Budaya)",
            ],
            index=0,
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

    st.divider()

    if video_siap_uji and video_siap_uji.exists():
        st.success(f"Video siap dianalisis: **{nama_video_uji}**")

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

with tab_arsip_baru:
    st.subheader("Tambah Klip Video ke Basis Arsip")
    st.write("Daftarkan video dokumentasi asli agar sistem dapat mendeteksi daur ulang di masa depan.")

    with st.form("form_arsip"):
        f_upload = st.file_uploader("Berkas Video Asli:", type=["mp4", "mkv", "webm", "avi"])
        f_judul = st.text_input("Judul / Deskripsi Peristiwa:", placeholder="Misal: Latihan Penanggulangan Banjir BPBD 2024")
        f_tanggal = st.date_input("Tanggal Asli Kejadian:")
        f_sumber = st.text_input("Sumber Resmi / Kanal Publikasi:", placeholder="Misal: Humas BNPB / YouTube Resmi")
        f_tautan = st.text_input("Tautan / Link Berita Asli:", placeholder="https://bnpb.go.id/...")
        btn_submit = st.form_submit_button("Simpan ke Arsip")

        if btn_submit:
            if not f_upload or not f_judul:
                st.error("Berkas video dan judul wajib diisi.")
            else:
                with st.spinner("Mengekstrak frame dan menyimpan hash ke database..."):
                    ext = Path(f_upload.name).suffix or ".mp4"
                    t_raw_path = TEMP_DIR / f"arsip_ui_{uuid.uuid4()}{ext}"
                    with open(t_raw_path, "wb") as f:
                        f.write(f_upload.getbuffer())

                    try:
                        info_baru = daftarkan_video_arsip(
                            db=db,
                            video_path=t_raw_path,
                            judul=f_judul,
                            tanggal_asli=str(f_tanggal),
                            sumber=f_sumber,
                            tautan=f_tautan,
                        )
                        st.success(f"Berhasil! Video '{f_judul}' didaftarkan dengan {info_baru['total_frame_hash']} keyframe.")
                    finally:
                        hapus_berkas_aman(t_raw_path)
