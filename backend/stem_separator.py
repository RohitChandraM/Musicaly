"""
Stem separation using Demucs (optional dependency).
If Demucs is not installed, separation is unavailable and callers receive
a clear error rather than a silent failure.
"""

import os
import subprocess
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


def _check_demucs_python() -> bool:
    try:
        import demucs  # noqa: F401
        return True
    except ImportError:
        return False


DEMUCS_AVAILABLE = _check_demucs_python() or shutil.which("demucs") is not None


class DemucsUnavailableError(Exception):
    """Raised when Demucs is not installed."""


def separate_stems(input_path: str, output_dir: str) -> dict[str, str]:
    """
    Separate a mixed song into vocal and instrumental stems using Demucs.

    Returns a dict:
        {"vocals": "/path/to/vocals.wav", "no_vocals": "/path/to/no_vocals.wav"}

    Raises DemucsUnavailableError if Demucs is not installed.
    Raises RuntimeError if separation fails.
    """
    if not DEMUCS_AVAILABLE:
        raise DemucsUnavailableError(
            "Demucs is not installed. Full-song separation is unavailable. "
            "Please upload a vocal stem instead, or install Demucs: "
            "pip install demucs"
        )

    os.makedirs(output_dir, exist_ok=True)

    try:
        cmd = [
            "python", "-m", "demucs",
            "--two-stems", "vocals",
            "--out", output_dir,
            "--mp3",
            input_path,
        ]
        logger.info("Running Demucs: %s", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            logger.error("Demucs stderr: %s", result.stderr)
            raise RuntimeError(f"Demucs failed: {result.stderr[-500:]}")

        stem_dir = _find_stem_dir(output_dir, Path(input_path).stem)
        vocals_path = _find_stem_file(stem_dir, "vocals")
        no_vocals_path = _find_stem_file(stem_dir, "no_vocals")

        return {"vocals": vocals_path, "no_vocals": no_vocals_path}

    except FileNotFoundError as exc:
        raise DemucsUnavailableError(
            "Could not launch Demucs. Make sure it is installed: pip install demucs"
        ) from exc


def _find_stem_dir(output_dir: str, track_name: str) -> str:
    """Locate the directory Demucs wrote stems into."""
    base = Path(output_dir)
    for model_dir in base.iterdir():
        if model_dir.is_dir():
            candidate = model_dir / track_name
            if candidate.exists():
                return str(candidate)
    for root, dirs, files in os.walk(output_dir):
        if any(f.startswith("vocals") for f in files):
            return root
    raise RuntimeError("Could not find Demucs output directory")


def _find_stem_file(stem_dir: str, stem_name: str) -> str:
    """Find a stem file (wav or mp3) by stem name."""
    for ext in (".wav", ".mp3", ".flac"):
        candidate = os.path.join(stem_dir, stem_name + ext)
        if os.path.exists(candidate):
            return candidate
    raise RuntimeError(f"Stem file '{stem_name}' not found in {stem_dir}")


def mix_vocal_with_instrumental(
    processed_vocal_path: str,
    instrumental_path: str,
    output_path: str,
    vocal_gain_db: float = 0.0,
) -> str:
    """
    Mix a processed vocal stem back with the instrumental using FFmpeg.
    Returns the path to the mixed output file.
    """
    gain_filter = f"volume={vocal_gain_db}dB" if vocal_gain_db != 0.0 else "anull"

    cmd = [
        "ffmpeg", "-y",
        "-i", instrumental_path,
        "-i", processed_vocal_path,
        "-filter_complex",
        f"[1:a]{gain_filter}[v];[0:a][v]amix=inputs=2:duration=first:dropout_transition=0[out]",
        "-map", "[out]",
        "-ar", "44100",
        "-sample_fmt", "s16",
        output_path,
    ]
    logger.info("Mixing stems with FFmpeg")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg mix failed: {result.stderr[-500:]}")
    return output_path
