"""
Stem separation using Demucs (optional dependency).
"""

import os
import subprocess
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


def _check_demucs_python():
    try:
        import demucs  # noqa: F401
        return True
    except ImportError:
        return False


DEMUCS_AVAILABLE = _check_demucs_python() or shutil.which("demucs") is not None


class DemucsUnavailableError(Exception):
    pass


def separate_stems(input_path, output_dir):
    if not DEMUCS_AVAILABLE:
        raise DemucsUnavailableError(
            "Demucs is not installed. Please upload a vocal stem instead, "
            "or install Demucs: pip install demucs"
        )
    os.makedirs(output_dir, exist_ok=True)
    try:
        cmd = ["python", "-m", "demucs", "--two-stems", "vocals", "--out", output_dir, "--mp3", input_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            raise RuntimeError(f"Demucs failed: {result.stderr[-500:]}")
        stem_dir = _find_stem_dir(output_dir, Path(input_path).stem)
        return {"vocals": _find_stem_file(stem_dir, "vocals"), "no_vocals": _find_stem_file(stem_dir, "no_vocals")}
    except FileNotFoundError as exc:
        raise DemucsUnavailableError("Could not launch Demucs: pip install demucs") from exc


def _find_stem_dir(output_dir, track_name):
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


def _find_stem_file(stem_dir, stem_name):
    for ext in (".wav", ".mp3", ".flac"):
        candidate = os.path.join(stem_dir, stem_name + ext)
        if os.path.exists(candidate):
            return candidate
    raise RuntimeError(f"Stem file '{stem_name}' not found in {stem_dir}")


def mix_vocal_with_instrumental(processed_vocal_path, instrumental_path, output_path, vocal_gain_db=0.0):
    gain_filter = f"volume={vocal_gain_db}dB" if vocal_gain_db != 0.0 else "anull"
    cmd = [
        "ffmpeg", "-y", "-i", instrumental_path, "-i", processed_vocal_path,
        "-filter_complex", f"[1:a]{gain_filter}[v];[0:a][v]amix=inputs=2:duration=first:dropout_transition=0[out]",
        "-map", "[out]", "-ar", "44100", "-sample_fmt", "s16", output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg mix failed: {result.stderr[-500:]}")
    return output_path
