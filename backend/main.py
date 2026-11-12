"""Entry point aplikasi FastAPI untuk backend WARAZ."""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Pastikan folder backend masuk ke sys.path agar impor `src.*` berjalan
# baik saat dijalankan dari root repo maupun dari dalam folder backend
_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from src.db.koneksi import init_db
    from src.video.router import router as video_router
    from src.clarification.router import router as clarification_router
    from src.manipulation.router import router as manipulation_router
except ImportError:
    from backend.src.db.koneksi import init_db
    from backend.src.video.router import router as video_router
    from backend.src.clarification.router import router as clarification_router
    from backend.src.manipulation.router import router as manipulation_router

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

# CORS middleware untuk frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
