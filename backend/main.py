"""Entry point aplikasi FastAPI untuk backend WARAZ."""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Pastikan folder backend dan root repo masuk ke sys.path agar impor `src.*`
# bekerja saat aplikasi dijalankan dari root repo, dari folder backend,
# atau saat di-deploy di platform seperti Vercel.
_BACKEND_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _BACKEND_DIR.parent
for _candidate in (_BACKEND_DIR, _PROJECT_ROOT):
    candidate_str = str(_candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db.koneksi import init_db
from src.video.router import router as video_router
from src.clarification.router import router as clarification_router
from src.manipulation.router import router as manipulation_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("waraz")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle handler untuk startup dan shutdown."""
    logger.info("Memulai WARAZ API...")
    init_db()
    yield
    logger.info("Mematikan WARAZ API...")


app = FastAPI(
    title="WARAZ API",
    description="Backend API untuk WARAZ — Deteksi Koordinasi, Klarifikasi Narasi.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware untuk frontend yang dipakai di Vercel dan lokal
allowed_origins = [
    "https://waraz.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\\.vercel\\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register router
app.include_router(video_router)
app.include_router(clarification_router)
app.include_router(manipulation_router)


@app.get("/", summary="Root API WARAZ")
def root():
    return {
        "sistem": "WARAZ",
        "tagline": "Deteksi Koordinasi, Klarifikasi Narasi",
        "versi": "0.1.0",
        "status": "aktif",
        "fitur_tersedia": [
            "F1: Issue Clarification (/api/v1/clarification)",
            "F2: Pelacak Video Daur Ulang (/api/v1/video)",
            "F3: Peta Teknik Manipulasi (/api/v1/manipulation)",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
