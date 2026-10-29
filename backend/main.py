"""Entry point aplikasi FastAPI untuk backend WARAZ."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db.koneksi import init_db
from src.video.router import router as video_router

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


@app.get("/", summary="Root API WARAZ")
def root():
    return {
        "sistem": "WARAZ",
        "tagline": "Deteksi Koordinasi, Klarifikasi Narasi",
        "versi": "0.1.0",
        "status": "aktif",
        "fitur_tersedia": [
            "F2: Pelacak Video Daur Ulang (/api/v1/video)",
        ],
    }
