"""Unified checker entry point for Feature 2: Recycled Video Tracker."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from ..db.connection import SessionLocal
from .service import detect_recycled_video

logger = logging.getLogger("waraz.video.checker")


def check_video(
    video_path: str | Path,
    db: Optional[Session] = None,
    kasus_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Checks whether an input video is recycled from the reference archive.

    Can be invoked with an existing DB session or automatically creates one.
    """
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if db is None:
        local_db = SessionLocal()
        try:
            return detect_recycled_video(
                db=local_db,
                video_path=path,
                kasus_id=kasus_id,
            )
        finally:
            local_db.close()
    else:
        return detect_recycled_video(
            db=db,
            video_path=path,
            kasus_id=kasus_id,
        )


# Backward compatibility alias
periksa_video = check_video

if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1:
        target = sys.argv[1]
        print(f"[*] Checking video: {target}")
        result = check_video(target)
        output = {k: v for k, v in result.items() if k != "detail_pasangan"}
        print(json.dumps(output, indent=2))
    else:
        print("Usage: python -m src.video.checker <path_to_video.mp4>")
