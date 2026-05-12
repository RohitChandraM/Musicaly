"""
Export processed audio to WAV and MP3 using soundfile and FFmpeg.
"""

import os
import subprocess
import numpy as np
import soundfile as sf
import logging

logger = logging.getLogger(__name__)


def export_wav(audio: np.ndarray, sr: int, output_path: str) -> str:
    """Write a float64 numpy array to a 16-bit PCM WAV file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    clipped = np.clip(audio, -1.0, 1.0)
    sf.write(output_path, clipped, sr, subtype="PCM_16")
    logger.info("Exported WAV: %s", output_path)
    return output_path


def export_mp3(wav_path: str, mp3_path: str, bitrate: str = "320k") -> str:
    """Convert a WAV file to MP3 using FFmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-i", wav_path,
        "-codec:a", "libmp3lame",
        "-b:a", bitrate,
        mp3_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg MP3 export failed: {result.stderr[-500:]}")
    logger.info("Exported MP3: %s", mp3_path)
    return mp3_path


def convert_to_wav(input_path: str, output_path: str, sample_rate: int = 44100) -> str:
    """
    Use FFmpeg to decode any supported format (MP3, FLAC, M4A, WAV) to a
    normalized 44.1 kHz, 16-bit stereo WAV for processing.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ar", str(sample_rate),
        "-ac", "2",
        "-sample_fmt", "s16",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(
            f"Could not decode audio file. "
            f"Make sure FFmpeg supports the format.\n{result.stderr[-300:]}"
        )
    logger.info("Converted to WAV: %s", output_path)
    return output_path
