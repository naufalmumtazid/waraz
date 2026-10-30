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

### 2. Jalankan Backend Server (FastAPI)
```bash
uv run uvicorn main:app --reload --port 8000
```

### 3. Jalankan Streamlit Demo UI
```bash
uv run streamlit run app_video_demo.py
```

### 4. Jalankan Pengujian (Pytest)
```bash
uv run pytest tests/ -v
```
