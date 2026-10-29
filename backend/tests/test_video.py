"""Pengujian otomatis untuk Fitur 2: Pelacak Video Daur Ulang.

Mencakup:
1. Ekstraksi frame & metadata video.
2. Perceptual hashing (pHash) dan perhitungan jarak Hamming.
3. Pencocokan urutan frame (sequence matching) dan ambang berurutan.
4. Deteksi video asli, dipotong (cropped), di-overlay teks, dan kontrol non-arsip.
5. REST API endpoint via TestClient FastAPI.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.skema import Base
from src.video.ekstraksi import dapatkan_info_video, ekstrak_frame
from src.video.hashing import hitung_dhash, hitung_phash, jarak_hamming, proses_video_ke_hash
from src.video.konfigurasi import STATUS_DAUR_ULANG, STATUS_TIDAK_DITEMUKAN
from src.video.layanan import daftarkan_video_arsip, deteksi_video_daur_ulang
from src.video.pencocokan import cocokkan_dua_sequence
from src.video.periksa import periksa_video
from src.video.skrip_demo import buat_video_sintetis

# Import FastAPI app
from main import app


class TestVideoPelacakDaurUlang(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = Path(tempfile.mkdtemp(prefix="waraz_test_"))

        # 1. Setup SQLite test database
        cls.db_path = cls.temp_dir / "test_waraz.db"
        cls.engine = create_engine(f"sqlite:///{cls.db_path}")
        Base.metadata.create_all(bind=cls.engine)
        cls.SessionClass = sessionmaker(bind=cls.engine)

        # 2. Buat video sintetis acuan arsip (durasi 8 detik)
        cls.video_arsip_path = cls.temp_dir / "arsip_latihan.mp4"
        buat_video_sintetis(
            cls.video_arsip_path,
            seed=101,
            durasi_detik=8,
            fps=10,
            judul_teks="SIMULASI KESIAPSIAGAAN BENCANA",
        )

        # 3. Buat varian daur ulang: Terpotong (detik 2.0 s/d 6.0)
        cls.video_potongan_path = cls.temp_dir / "daur_ulang_potongan.mp4"
        buat_video_sintetis(
            cls.video_potongan_path,
            seed=101,
            durasi_detik=8,
            fps=10,
            judul_teks="SIMULASI KESIAPSIAGAAN BENCANA",
            mulai_detik=2.0,
            selesai_detik=6.0,
        )

        # 4. Buat varian daur ulang: Teks Banner Palsu
        cls.video_banner_path = cls.temp_dir / "daur_ulang_banner.mp4"
        buat_video_sintetis(
            cls.video_banner_path,
            seed=101,
            durasi_detik=8,
            fps=10,
            judul_teks="SIMULASI KESIAPSIAGAAN BENCANA",
            overlay_tambahan="GEMPA BUMI DAHSYAT BARU SAJA TERJADI!",
        )

        # 5. Buat kontrol non-arsip (video baru/orisinal)
        cls.video_orisinal_path = cls.temp_dir / "bukan_arsip.mp4"
        buat_video_sintetis(
            cls.video_orisinal_path,
            seed=888,
            durasi_detik=8,
            fps=10,
            judul_teks="PAGELARAN SENI DAN BUDAYA DAERAH",
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def setUp(self):
        self.session = self.SessionClass()

    def tearDown(self):
        self.session.close()

    def test_01_ekstraksi_dan_info_video(self):
        """Memverifikasi ekstraksi frame dan pengambilan metadata video."""
        info = dapatkan_info_video(self.video_arsip_path)
        self.assertGreater(info["durasi_detik"], 6.0)
        self.assertEqual(info["lebar"], 640)
        self.assertEqual(info["tinggi"], 360)

        frames = ekstrak_frame(self.video_arsip_path, interval_detik=2.0)
        self.assertGreaterEqual(len(frames), 4)
        self.assertIsInstance(frames[0]["image"], Image.Image)
        self.assertEqual(frames[0]["urutan"], 0)

    def test_02_hashing_dan_jarak_hamming(self):
        """Memverifikasi perhitungan pHash, dHash, dan jarak Hamming."""
        # Buat dua gambar dengan pola visual berbeda
        img1 = Image.new("RGB", (100, 100), color=(255, 255, 255))
        d1 = ImageDraw.Draw(img1)
        d1.rectangle([10, 10, 90, 90], fill=(0, 0, 0))

        img2 = Image.new("RGB", (100, 100), color=(255, 255, 255))
        d2 = ImageDraw.Draw(img2)
        d2.rectangle([10, 10, 90, 90], fill=(0, 0, 0))

        img3 = Image.new("RGB", (100, 100), color=(255, 255, 255))
        d3 = ImageDraw.Draw(img3)
        d3.ellipse([10, 10, 90, 90], fill=(0, 0, 0))

        h1 = hitung_phash(img1)
        h2 = hitung_phash(img2)
        h3 = hitung_phash(img3)

        # Dua gambar identik harus berjarak 0
        self.assertEqual(jarak_hamming(h1, h2), 0)

        # Gambar berbeda pola memiliki jarak Hamming > 0
        self.assertGreater(jarak_hamming(h1, h3), 0)

    def test_03_cocokkan_dua_sequence(self):
        """Menguji logika sequence matching berurutan."""
        base = ["1111111111111111", "2222222222222222", "3333333333333333", "4444444444444444", "5555555555555555"]
        sub = ["2222222222222222", "3333333333333333", "4444444444444444"]
        acak = ["9999999999999999", "8888888888888888", "7777777777777777"]

        res_sub = cocokkan_dua_sequence(sub, base, ambang_hamming=0, min_berurutan=3)
        self.assertTrue(res_sub["cocok"])
        self.assertEqual(res_sub["max_consecutive"], 3)
        self.assertEqual(res_sub["total_cocok"], 3)

        res_acak = cocokkan_dua_sequence(acak, base, ambang_hamming=0, min_berurutan=3)
        self.assertFalse(res_acak["cocok"])

    def test_04_pipeline_daur_ulang_database(self):
        """Menguji end-to-end pendaftaran arsip dan deteksi daur ulang."""
        info_arsip = daftarkan_video_arsip(
            db=self.session,
            video_path=self.video_arsip_path,
            judul="Dokumentasi Latihan BPBD",
            tanggal_asli="2023-05-10",
            sumber="Humas Penanggulangan Bencana",
            tautan="https://bpbd.contoh.go.id/latihan-2023",
        )
        self.assertIn("id", info_arsip)
        self.assertGreater(info_arsip["total_frame_hash"], 0)

        # Uji video daur ulang versi potongan (cropped in time)
        hasil_potongan = deteksi_video_daur_ulang(
            db=self.session,
            video_path=self.video_potongan_path,
        )
        self.assertEqual(hasil_potongan["status"], STATUS_DAUR_ULANG)
        self.assertIsNotNone(hasil_potongan["arsip_tercocok"])
        self.assertEqual(hasil_potongan["arsip_tercocok"]["id"], info_arsip["id"])
        self.assertGreaterEqual(hasil_potongan["consecutive_run"], 2)

        # Uji fungsi utama periksa_video()
        hasil_periksa = periksa_video(
            video_path=self.video_potongan_path,
            db=self.session,
        )
        self.assertEqual(hasil_periksa["status"], STATUS_DAUR_ULANG)
        self.assertEqual(hasil_periksa["arsip_tercocok"]["id"], info_arsip["id"])

        # Uji video daur ulang versi overlay banner
        hasil_banner = deteksi_video_daur_ulang(
            db=self.session,
            video_path=self.video_banner_path,
        )
        self.assertEqual(hasil_banner["status"], STATUS_DAUR_ULANG)
        self.assertEqual(hasil_banner["arsip_tercocok"]["id"], info_arsip["id"])

        # Uji video orisinal / non-arsip (harus negatif)
        hasil_orisinal = deteksi_video_daur_ulang(
            db=self.session,
            video_path=self.video_orisinal_path,
        )
        self.assertEqual(hasil_orisinal["status"], STATUS_TIDAK_DITEMUKAN)
        self.assertIsNone(hasil_orisinal["arsip_tercocok"])

    def test_05_api_endpoints(self):
        """Memverifikasi endpoint REST API FastAPI menggunakan context manager."""
        with TestClient(app) as client:
            # 1. Test root API
            resp_root = client.get("/")
            self.assertEqual(resp_root.status_code, 200)
            self.assertEqual(resp_root.json()["sistem"], "WARAZ")

            # 2. Test seed-demo
            resp_seed = client.post("/api/v1/video/seed-demo")
            self.assertEqual(resp_seed.status_code, 200)
            data_seed = resp_seed.json()
            self.assertEqual(data_seed["status"], "sukses")

            # 3. Test list arsip
            resp_list = client.get("/api/v1/video/arsip")
            self.assertEqual(resp_list.status_code, 200)
            self.assertIsInstance(resp_list.json(), list)
            self.assertGreater(len(resp_list.json()), 0)

            # 4. Test deteksi via file upload
            with open(self.video_potongan_path, "rb") as vf:
                resp_deteksi = client.post(
                    "/api/v1/video/deteksi",
                    files={"file": ("potongan.mp4", vf, "video/mp4")},
                )
            self.assertEqual(resp_deteksi.status_code, 200)
            data_deteksi = resp_deteksi.json()
            self.assertIn("status", data_deteksi)
            self.assertIn("skor", data_deteksi)
            self.assertIn("keyakinan", data_deteksi)


if __name__ == "__main__":
    unittest.main()
