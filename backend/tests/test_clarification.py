"""Pengujian otomatis untuk Fitur 1: Issue Clarification.

Mencakup:
1. Similarity scoring & hasil /check (sudah_diklarifikasi, mirip, belum_ditemukan).
2. Submisi klaim publik (status menunggu).
3. Login admin dari env WARAZ_ADMIN_* (valid & invalid).
4. Admin review: approve mempromosikan klaim ke basis klarifikasi, reject menolak.
5. Proteksi endpoint admin tanpa/invalid token.
"""

import os
import tempfile
import unittest
from pathlib import Path

# Konfigurasi admin untuk pengujian (disetel sebelum import app/config)
os.environ.setdefault("WARAZ_ADMIN_EMAIL", "admin@waraz.local")
os.environ.setdefault("WARAZ_ADMIN_PASSWORD", "waraz-admin-2026")
os.environ.setdefault("WARAZ_ADMIN_TOKEN", "waraz-demo-admin-token")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.koneksi import get_db
from src.db.skema import Base
from main import app

ADMIN_TOKEN = "waraz-demo-admin-token"


class TestIssueClarification(unittest.TestCase):
    temp_dir = None

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = Path(tempfile.mkdtemp(prefix="waraz_clarif_test_"))
        cls.db_path = cls.temp_dir / "test_waraz.db"
        cls.engine = create_engine(f"sqlite:///{cls.db_path}")
        Base.metadata.create_all(bind=cls.engine)
        cls.SessionClass = sessionmaker(bind=cls.engine)

        def override_get_db():
            db = cls.SessionClass()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.pop(get_db, None)

    def setUp(self):
        from src.db.skema import Clarification, ClarificationResult, PublicClaim

        with self.SessionClass() as db:
            for table in (ClarificationResult, PublicClaim, Clarification):
                db.query(table).delete()
            db.commit()

    def seed_klarifikasi(self, klaim: str, ringkasan: str = "", sumber: str = "Wikipedia"):
        from src.db.skema import Clarification

        with self.SessionClass() as db:
            db.add(
                Clarification(
                    klaim=klaim,
                    status="aktif",
                    ringkasan=ringkasan,
                    tanggal="2025-01-01",
                    sumber=sumber,
                    tautan="https://contoh.ORG/klarifikasi",
                )
            )
            db.commit()

    # ── /check ────────────────────────────────────────────

    def test_check_isi_kosong(self):
        res = self.client.post("/api/v1/clarification/check", json={"issue": "   "})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status_result"], "tidak_ada_isi")

    def test_check_belum_ditemukan(self):
        res = self.client.post(
            "/api/v1/clarification/check",
            json={"issue": "Ngangkahtopter kiamat jahanam suhu 40 derajat topan terbalik seduh materi monokotil."},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status_result"], "belum_ditemukan")
        self.assertEqual(data["matches"], [])

    def test_check_ditemukan_persis(self):
        self.seed_klarifikasi(
            "Lele dikira cubang mati satu tak jailand dan berjuang menghindar.",
            ringkasan="Klarifikasi tentang kesalahan kapital dan typo isu lele.",
        )
        res = self.client.post(
            "/api/v1/clarification/check",
            json={"issue": "Lele dikira cubang mati satu tak jailand dan berjuang menghindar."},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status_result"], "sudah_diklarifikasi")
        self.assertTrue(data["matches"])
        self.assertGreaterEqual(data["matches"][0]["score"], 0.98)

    # ── /submit ───────────────────────────────────────────

    def test_submit_klaim_publik(self):
        res = self.client.post(
            "/api/v1/clarification/submit",
            json={
                "claim": "Kerang ajaib bisa menggugurkan janin saat banjir bandang.",
                "summary": "Benang merah cerita isu lokal yang menyebar di WA.",
                "category": "mitos",
                "anonymous": False,
                "submitter_alias": "nurul",
            },
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "menunggu")
        self.assertEqual(data["submitter_alias"], "nurul")
        self.assertFalse(data["anonymous"])
        self.assertIn("message", data)

    def test_submit_klaim_kosong(self):
        res = self.client.post("/api/v1/clarification/submit", json={"claim": " "})
        self.assertEqual(res.status_code, 400)

    # ── /admin/login ──────────────────────────────────────

    def test_login_admin_valid(self):
        res = self.client.post(
            "/api/v1/clarification/admin/login",
            json={"email": "admin@waraz.local", "password": "waraz-admin-2026"},
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["token"], ADMIN_TOKEN)

    def test_login_admin_salah(self):
        res = self.client.post(
            "/api/v1/clarification/admin/login",
            json={"email": "admin@waraz.local", "password": "password-salah"},
        )
        self.assertEqual(res.status_code, 401)
        self.assertIn("salah", res.json()["detail"])

    # ── proteksi endpoint admin ───────────────────────────

    def test_admin_claims_tanpa_token(self):
        res = self.client.get("/api/v1/clarification/admin/claims")
        self.assertEqual(res.status_code, 401)

    def test_admin_flow_approve(self):
        submit = self.client.post(
            "/api/v1/clarification/submit",
            json={"claim": "Manual kiamat menurut habar data kerja lu kedua pantura.", "category": "hoaks"},
        )
        claim_id = submit.json()["id"]

        daftar = self.client.get(
            "/api/v1/clarification/admin/claims",
            headers={"x-admin-token": ADMIN_TOKEN},
        )
        self.assertEqual(daftar.status_code, 200)
        self.assertTrue(any(c["id"] == claim_id for c in daftar.json()))

        res = self.client.post(
            f"/api/v1/clarification/admin/claims/{claim_id}/review",
            headers={"x-admin-token": ADMIN_TOKEN},
            json={"decision": "approve", "review_note": "Sudah diverifikasi tim."},
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "disetujui")

        # Klaim yang disetujui harus bisa ditemukan via /check
        cek = self.client.post(
            "/api/v1/clarification/check",
            json={"issue": "Manual kiamat menurut habar data kerja lu kedua pantura."},
        )
        self.assertEqual(cek.json()["status_result"], "sudah_diklarifikasi")

        # Tidak bisa direview ulang karena sudah bukan status menunggu
        res = self.client.post(
            f"/api/v1/clarification/admin/claims/{claim_id}/review",
            headers={"x-admin-token": ADMIN_TOKEN},
            json={"decision": "reject", "review_note": None},
        )
        self.assertEqual(res.status_code, 409)

    def test_admin_flow_reject(self):
        submit = self.client.post(
            "/api/v1/clarification/submit",
            json={"claim": "Tuyul digital mencuri arsip publik SiO pocong muka tujuh belas.", "category": "urban_legend"},
        )
        claim_id = submit.json()["id"]

        res = self.client.post(
            f"/api/v1/clarification/admin/claims/{claim_id}/review",
            headers={"x-admin-token": ADMIN_TOKEN},
            json={"decision": "reject"},
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ditolak")

    def test_review_claim_tidak_ada(self):
        res = self.client.post(
            "/api/v1/clarification/admin/claims/id-palsu/review",
            headers={"x-admin-token": ADMIN_TOKEN},
            json={"decision": "approve"},
        )
        self.assertEqual(res.status_code, 404)

    def test_review_decision_tidak_valid(self):
        submit = self.client.post(
            "/api/v1/clarification/submit",
            json={"claim": "Isu dummy untuk decision invalid.", "category": "lainnya"},
        )
        claim_id = submit.json()["id"]
        res = self.client.post(
            f"/api/v1/clarification/admin/claims/{claim_id}/review",
            headers={"x-admin-token": ADMIN_TOKEN},
            json={"decision": "salah"},
        )
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()
