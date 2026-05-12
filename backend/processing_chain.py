"""
Core audio processing chain for Vocal Humanizer AI.
"""

import numpy as np
import soundfile as sf
import librosa
from scipy import signal
import os
import logging

logger = logging.getLogger(__name__)


def _biquad_peaking(fc, gain_db, q, fs):
    A = 10 ** (gain_db / 40.0)
    w0 = 2 * np.pi * fc / fs
    alpha = np.sin(w0) / (2 * q)
    b = [1 + alpha * A, -2 * np.cos(w0), 1 - alpha * A]
    a = [1 + alpha / A, -2 * np.cos(w0), 1 - alpha / A]
    return np.array(b), np.array(a)


def _biquad_highshelf(fc, gain_db, fs, slope=0.7):
    A = 10 ** (gain_db / 40.0)
    w0 = 2 * np.pi * fc / fs
    alpha = (np.sin(w0) / 2) * np.sqrt((A + 1 / A) * (1 / slope - 1) + 2)
    cosw = np.cos(w0)
    sqrtA = np.sqrt(A)
    b = [
        A * ((A + 1) + (A - 1) * cosw + 2 * sqrtA * alpha),
        -2 * A * ((A - 1) + (A + 1) * cosw),
        A * ((A + 1) + (A - 1) * cosw - 2 * sqrtA * alpha),
    ]
    a = [
        (A + 1) - (A - 1) * cosw + 2 * sqrtA * alpha,
        2 * ((A - 1) - (A + 1) * cosw),
        (A + 1) - (A - 1) * cosw - 2 * sqrtA * alpha,
    ]
    return np.array(b), np.array(a)


def apply_biquad(audio, b, a):
    if audio.ndim == 1:
        return signal.lfilter(b, a, audio)
    return np.stack([signal.lfilter(b, a, ch) for ch in audio.T], axis=1)


def apply_highpass(audio, cutoff, sr, order=2):
    nyq = sr / 2.0
    sos = signal.butter(order, cutoff / nyq, btype="high", output="sos")
    if audio.ndim == 1:
        return signal.sosfilt(sos, audio)
    return np.stack([signal.sosfilt(sos, ch) for ch in audio.T], axis=1)


def apply_peaking_eq(audio, fc, gain_db, q, sr):
    if abs(gain_db) < 0.05:
        return audio
    b, a = _biquad_peaking(fc, gain_db, q, sr)
    return apply_biquad(audio, b, a)


def apply_highshelf(audio, fc, gain_db, sr):
    if abs(gain_db) < 0.05:
        return audio
    b, a = _biquad_highshelf(fc, gain_db, sr)
    return apply_biquad(audio, b, a)


def _bandpass_audio(audio, low, high, sr):
    nyq = sr / 2.0
    sos = signal.butter(2, [low / nyq, high / nyq], btype="band", output="sos")
    if audio.ndim == 1:
        return signal.sosfilt(sos, audio)
    return np.stack([signal.sosfilt(sos, ch) for ch in audio.T], axis=1)


def _envelope_follower(audio, sr, attack_ms=5.0, release_ms=50.0):
    attack_coef = np.exp(-1.0 / (sr * attack_ms / 1000.0))
    release_coef = np.exp(-1.0 / (sr * release_ms / 1000.0))
    mono = audio if audio.ndim == 1 else np.mean(audio, axis=1)
    rectified = np.abs(mono)
    envelope = np.zeros_like(rectified)
    env = 0.0
    for i, x in enumerate(rectified):
        if x > env:
            env = attack_coef * env + (1 - attack_coef) * x
        else:
            env = release_coef * env + (1 - release_coef) * x
        envelope[i] = env
    return envelope


def dynamic_harshness_reduction(audio, sr, fc, q, threshold_db, max_reduction_db):
    if max_reduction_db < 0.1:
        return audio
    low = fc / (2 ** (1 / (2 * q)))
    high = min(fc * (2 ** (1 / (2 * q))), sr * 0.45)
    sidechain = _bandpass_audio(audio, low, high, sr)
    envelope = _envelope_follower(sidechain, sr, attack_ms=3.0, release_ms=40.0)
    threshold_lin = 10 ** (threshold_db / 20.0)
    excess = np.maximum(envelope - threshold_lin, 0.0) / (threshold_lin + 1e-9)
    gr_db = -np.minimum(excess * max_reduction_db, max_reduction_db)
    block_size = 512
    result = audio.copy()
    n_samples = audio.shape[0]
    for start in range(0, n_samples, block_size):
        end = min(start + block_size, n_samples)
        avg_gr = float(np.mean(gr_db[start:end]))
        if avg_gr < -0.05:
            b, a = _biquad_peaking(fc, avg_gr, q, sr)
            block = audio[start:end] if audio.ndim == 1 else audio[start:end, :]
            result[start:end] = apply_biquad(block, b, a)
    return result


def de_esser(audio, sr, fc, q, threshold_db, max_reduction_db):
    return dynamic_harshness_reduction(audio, sr, fc, q, threshold_db, max_reduction_db)


def soft_saturation(audio, drive, mix):
    if mix < 0.001:
        return audio
    driven = np.tanh(audio * drive) / np.tanh(drive) if drive > 1.0 else audio
    return (1.0 - mix) * audio + mix * driven


def add_ambience(audio, sr, room_size, damping, wet_level, dry_level):
    if wet_level < 0.001:
        return audio
    try:
        from pedalboard import Pedalboard, Reverb
        board = Pedalboard([Reverb(room_size=room_size, damping=damping, wet_level=wet_level, dry_level=dry_level)])
        mono = audio.ndim == 1
        stereo = np.stack([audio, audio], axis=0) if mono else audio.T
        processed = board(stereo.astype(np.float32), sr)
        result = np.mean(processed, axis=0) if mono else processed.T
        return result.astype(np.float64)
    except ImportError:
        delay_samples = int(sr * 0.025 * room_size)
        if delay_samples < 1:
            return audio
        decay = 1.0 - damping * 0.5
        ir = np.zeros(delay_samples + 1)
        ir[0] = 1.0
        ir[-1] = decay * 0.3
        mono_audio = audio if audio.ndim == 1 else np.mean(audio, axis=1)
        reverb_tail = np.convolve(mono_audio, ir, mode="full")[:len(mono_audio)]
        wet = reverb_tail * wet_level
        dry = audio * dry_level
        return np.clip(dry + (wet[:, None] if audio.ndim > 1 else wet), -1.0, 1.0)


def peak_normalize(audio, target_db=-1.0):
    peak = np.max(np.abs(audio))
    if peak < 1e-9:
        return audio
    return audio * (10 ** (target_db / 20.0) / peak)


def lufs_normalize(audio, sr, target_lufs=-14.0):
    mono = audio if audio.ndim == 1 else np.mean(audio, axis=1)
    rms = np.sqrt(np.mean(mono ** 2))
    if rms < 1e-9:
        return audio
    current_lufs_approx = 20 * np.log10(rms) - 0.691
    gain_db = np.clip(target_lufs - current_lufs_approx, -20.0, 12.0)
    return audio * (10 ** (gain_db / 20.0))


def process_vocal(audio, sr, preset):
    p = preset
    audio = apply_highpass(audio, p["hp_freq"], sr, order=p.get("hp_order", 2))
    audio = peak_normalize(audio, target_db=-3.0)
    audio = apply_peaking_eq(audio, p["body_freq"], p["body_gain_db"], p["body_q"], sr)
    audio = apply_peaking_eq(audio, p["mud_freq"], p["mud_gain_db"], p["mud_q"], sr)
    audio = apply_peaking_eq(audio, p["nasal_freq"], p["nasal_gain_db"], p["nasal_q"], sr)
    audio = apply_peaking_eq(audio, p["presence_freq"], p["presence_gain_db"], p["presence_q"], sr)
    audio = dynamic_harshness_reduction(audio, sr, fc=p["harsh_freq"], q=p["harsh_q"],
                                        threshold_db=p["harsh_threshold_db"], max_reduction_db=p["harsh_reduction_db"])
    audio = de_esser(audio, sr, fc=p["dess_freq"], q=p["dess_q"],
                     threshold_db=p["dess_threshold_db"], max_reduction_db=p["dess_reduction_db"])
    audio = soft_saturation(audio, drive=p["sat_drive"], mix=p["sat_mix"])
    audio = apply_highshelf(audio, p["air_freq"], p["air_gain_db"], sr)
    audio = add_ambience(audio, sr, room_size=p["reverb_room_size"], damping=p["reverb_damping"],
                         wet_level=p["reverb_wet_level"], dry_level=p["reverb_dry_level"])
    audio = lufs_normalize(audio, sr, target_lufs=-14.0)
    audio = peak_normalize(audio, target_db=-1.0)
    return np.clip(audio, -1.0, 1.0)
