# WARAZ Backend

Backend API dan engine analisis untuk WARAZ (Deteksi Koordinasi, Klarifikasi Narasi).

## Menjalankan dengan `uv`

### 1. Buat Virtual Environment & Install Dependensi
```bash
# Dari direktori backend
uv sync
# atau
uv pip install -r requirements.txt
```

### 2. Jalankan Backend Server (FastAPI REST API)
```bash
uv run uvicorn main:app --reload --port 8000
```
Dokumentasi Swagger API interaktif tersedia di: `http://localhost:8000/docs`

### 3. Jalankan Pengujian (Pytest)
```bash
uv run pytest tests/ -v
```

*Catatan: Antarmuka pengguna (UI) kini sepenuhnya dipisahkan ke modul `frontend/` (Next.js).*
