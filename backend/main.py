"""
Vocal Humanizer AI — FastAPI backend.
Endpoints: /upload, /process, /status/{job_id}, /download/{file_id}
"""

import os
import uuid
import time
import logging
import asyncio
import threading
from typing import Optional

import numpy as np
import soundfile as sf
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from upload_handler import save_upload, get_upload_path, get_processed_path, start_cleanup_thread, TEMP_DIR
from processing_chain import process_vocal
from presets import get_preset, scale_preset
from export_handler import convert_to_wav, export_wav, export_mp3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Vocal Humanizer AI",
    description="One-click polish for AI vocals.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store  {job_id: {"status": str, "file_id": str, "error": str}}
jobs: dict[str, dict] = {}
jobs_lock = threading.Lock()


@app.on_event("startup")
def on_startup():
    os.makedirs(TEMP_DIR, exist_ok=True)
    start_cleanup_thread()


# ---------------------------------------------------------------------------
# POST /upload
# ---------------------------------------------------------------------------

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Accept an audio file and return a file_id for later processing."""
    meta = await save_upload(file)
    return {
        "file_id": meta["file_id"],
        "original_name": meta["original_name"],
        "size_bytes": meta["size_bytes"],
        "extension": meta["extension"],
    }


# ---------------------------------------------------------------------------
# POST /process
# ---------------------------------------------------------------------------

@app.post("/process")
async def process_file(body: dict, background_tasks: BackgroundTasks):
    """
    Start a processing job.
    Body: {
        "file_id": str,
        "input_type": "vocal_stem" | "full_song" | "auto",
        "preset": "natural" | "warm" | "rap_punchy",
        "strength": float  (0.0 – 1.0)
    }
    Returns: {"job_id": str}
    """
    file_id = body.get("file_id")
    input_type = body.get("input_type", "auto")
    preset_name = body.get("preset", "natural")
    strength = float(body.get("strength", 0.75))
    strength = max(0.0, min(1.0, strength))

    if not file_id:
        raise HTTPException(status_code=400, detail="file_id is required.")

    upload_path = get_upload_path(file_id)
    if not upload_path:
        raise HTTPException(status_code=404, detail="File not found. Please upload again.")

    job_id = str(uuid.uuid4())
    with jobs_lock:
        jobs[job_id] = {"status": "queued", "file_id": file_id, "error": None, "progress": 0}

    background_tasks.add_task(
        _run_job,
        job_id=job_id,
        file_id=file_id,
        upload_path=upload_path,
        input_type=input_type,
        preset_name=preset_name,
        strength=strength,
    )

    return {"job_id": job_id}


def _run_job(
    job_id: str,
    file_id: str,
    upload_path: str,
    input_type: str,
    preset_name: str,
    strength: float,
):
    """Background worker that runs the full processing chain."""

    def set_status(status: str, progress: int = 0, error: str = None):
        with jobs_lock:
            jobs[job_id]["status"] = status
            jobs[job_id]["progress"] = progress
            if error:
                jobs[job_id]["error"] = error

    try:
        set_status("processing", progress=5)

        # --- Step 1: Determine if we need stem separation ---
        needs_separation = False
        if input_type == "full_song":
            needs_separation = True
        elif input_type == "auto":
            needs_separation = _looks_like_full_song(upload_path)

        vocal_path = upload_path
        instrumental_path = None

        if needs_separation:
            set_status("processing", progress=10)
            try:
                from stem_separator import separate_stems, DemucsUnavailableError
                stems = separate_stems(upload_path, output_dir=TEMP_DIR)
                vocal_path = stems["vocals"]
                instrumental_path = stems["no_vocals"]
                logger.info("Separation done. Vocals: %s", vocal_path)
            except Exception as exc:
                if "DemucsUnavailable" in type(exc).__name__ or "not installed" in str(exc).lower():
                    set_status("processing", progress=10)
                    logger.warning("Demucs unavailable — processing as vocal stem: %s", exc)
                    vocal_path = upload_path
                    instrumental_path = None
                    with jobs_lock:
                        jobs[job_id]["warning"] = (
                            "Demucs is not installed — processed the full file as a vocal stem. "
                            "For best results with full songs, install Demucs: pip install demucs"
                        )
                else:
                    raise

        set_status("processing", progress=25)

        # --- Step 2: Convert vocal to 44.1 kHz WAV ---
        wav_input = os.path.join(TEMP_DIR, f"{file_id}_input.wav")
        convert_to_wav(vocal_path, wav_input, sample_rate=44100)

        set_status("processing", progress=35)

        # --- Step 3: Load audio ---
        audio, sr = sf.read(wav_input, dtype="float64", always_2d=False)
        logger.info("Loaded audio: %d samples @ %d Hz, shape=%s", len(audio), sr, audio.shape)

        set_status("processing", progress=45)

        # --- Step 4: Build scaled preset ---
        preset = get_preset(preset_name)
        scaled = scale_preset(preset, strength)

        # --- Step 5: Process ---
        processed = process_vocal(audio, sr, scaled)

        set_status("processing", progress=80)

        # --- Step 6: Mix back with instrumental if we separated ---
        if instrumental_path is not None:
            from stem_separator import mix_vocal_with_instrumental
            processed_vocal_wav = os.path.join(TEMP_DIR, f"{file_id}_processed_vocal.wav")
            export_wav(processed, sr, processed_vocal_wav)
            mixed_output = os.path.join(TEMP_DIR, f"{file_id}_processed.wav")
            mix_vocal_with_instrumental(processed_vocal_wav, instrumental_path, mixed_output)
        else:
            wav_out = os.path.join(TEMP_DIR, f"{file_id}_processed.wav")
            export_wav(processed, sr, wav_out)

        set_status("processing", progress=90)

        # --- Step 7: Export MP3 ---
        wav_out = os.path.join(TEMP_DIR, f"{file_id}_processed.wav")
        mp3_out = os.path.join(TEMP_DIR, f"{file_id}_processed.mp3")
        export_mp3(wav_out, mp3_out)

        set_status("done", progress=100)
        logger.info("Job %s complete for file %s", job_id, file_id)

    except Exception as exc:
        logger.exception("Job %s failed: %s", job_id, exc)
        set_status("error", progress=0, error=str(exc))


def _looks_like_full_song(path: str) -> bool:
    """Rough heuristic: stereo file longer than 90 seconds = probably a full song."""
    try:
        info = sf.info(path)
        return info.channels >= 2 and info.duration > 90
    except Exception:
        return False


# ---------------------------------------------------------------------------
# GET /status/{job_id}
# ---------------------------------------------------------------------------

@app.get("/status/{job_id}")
def get_status(job_id: str):
    """Poll job status and progress."""
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


# ---------------------------------------------------------------------------
# GET /download/{file_id}
# ---------------------------------------------------------------------------

@app.get("/download/{file_id}")
def download_file(file_id: str, fmt: str = "wav"):
    """
    Download a processed file.
    Query param: fmt=wav (default) or fmt=mp3
    """
    fmt = fmt.lower()
    if fmt not in ("wav", "mp3"):
        raise HTTPException(status_code=400, detail="fmt must be 'wav' or 'mp3'.")

    path = get_processed_path(file_id, fmt)
    if not path:
        raise HTTPException(
            status_code=404,
            detail=f"Processed {fmt.upper()} file not found. Has processing completed?",
        )

    media_type = "audio/wav" if fmt == "wav" else "audio/mpeg"
    filename = f"humanized_vocal.{fmt}"
    return FileResponse(path, media_type=media_type, filename=filename)


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "service": "Vocal Humanizer AI"}
