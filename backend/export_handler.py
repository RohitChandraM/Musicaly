"""
Export processed audio to WAV and MP3 using soundfile and FFmpeg.
"""

import os
import subprocess
import numpy as np
import soundfile as sf
import logging

logger = logging.getLogger(__name__)


def export_wav(audio, sr, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, np.clip(audio, -1.0, 1.0), sr, subtype="PCM_16")
    return output_path


def export_mp3(wav_path, mp3_path, bitrate="320k"):
    cmd = ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-b:a", bitrate, mp3_path]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg MP3 export failed: {result.stderr[-500:]}")
    return mp3_path


def convert_to_wav(input_path, output_path, sample_rate=44100):
    cmd = ["ffmpeg", "-y", "-i", input_path, "-ar", str(sample_rate), "-ac", "2", "-sample_fmt", "s16", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"Could not decode audio file.\n{result.stderr[-300:]}")
    return output_path
