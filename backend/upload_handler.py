"""
Upload handling: validation, safe temp storage, and automatic cleanup.
"""

import os
import uuid
import time
import asyncio
import logging
import threading
from pathlib import Path
from typing import Optional

from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a", ".aac", ".ogg"}
MAX_FILE_SIZE_MB = 200
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
TEMP_DIR = os.path.join(os.path.dirname(__file__), "..", "temp_files")
FILE_TTL_SECONDS = 3600  # Auto-delete files older than 1 hour


def ensure_temp_dir() -> str:
    os.makedirs(TEMP_DIR, exist_ok=True)
    return TEMP_DIR


def _safe_filename(original: str, uid: str) -> str:
    """Generate a safe temp filename from a UUID + original extension."""
    ext = Path(original).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Accepted: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    return f"{uid}{ext}"


async def save_upload(file: UploadFile) -> dict:
    """
    Validate and save an uploaded file to disk.
    Returns metadata dict with file_id, path, original_name, size.
    """
    ensure_temp_dir()

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Please upload WAV, MP3, FLAC, or M4A.",
        )

    file_id = str(uuid.uuid4())
    safe_name = _safe_filename(file.filename, file_id)
    dest_path = os.path.join(TEMP_DIR, safe_name)

    total_bytes = 0
    chunk_size = 1024 * 1024  # 1 MB
    with open(dest_path, "wb") as f:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            total_bytes += len(chunk)
            if total_bytes > MAX_FILE_SIZE_BYTES:
                f.close()
                os.remove(dest_path)
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB} MB.",
                )
            f.write(chunk)

    logger.info("Saved upload: %s (%d bytes)", dest_path, total_bytes)
    return {
        "file_id": file_id,
        "path": dest_path,
        "original_name": file.filename,
        "size_bytes": total_bytes,
        "extension": ext,
    }


def get_upload_path(file_id: str) -> Optional[str]:
    """Locate an uploaded file by its UUID (any extension)."""
    for ext in ALLOWED_EXTENSIONS:
        candidate = os.path.join(TEMP_DIR, f"{file_id}{ext}")
        if os.path.exists(candidate):
            return candidate
    return None


def get_processed_path(file_id: str, fmt: str = "wav") -> Optional[str]:
    """Locate a processed output file by file_id and format."""
    candidate = os.path.join(TEMP_DIR, f"{file_id}_processed.{fmt}")
    return candidate if os.path.exists(candidate) else None


# ---------------------------------------------------------------------------
# Background cleanup thread
# ---------------------------------------------------------------------------

def _cleanup_worker():
    """Delete temp files older than FILE_TTL_SECONDS. Runs in background."""
    while True:
        try:
            now = time.time()
            for fname in os.listdir(TEMP_DIR):
                fpath = os.path.join(TEMP_DIR, fname)
                try:
                    if os.path.isfile(fpath) and (now - os.path.getmtime(fpath)) > FILE_TTL_SECONDS:
                        os.remove(fpath)
                        logger.info("Cleaned up: %s", fpath)
                except OSError:
                    pass
        except Exception as exc:
            logger.warning("Cleanup error: %s", exc)
        time.sleep(300)  # Run every 5 minutes


def start_cleanup_thread():
    thread = threading.Thread(target=_cleanup_worker, daemon=True)
    thread.start()
    logger.info("File cleanup thread started (TTL=%ds)", FILE_TTL_SECONDS)
