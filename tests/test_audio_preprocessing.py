"""
Unit Tests for Audio Preprocessor and Voice Activity Detection.
"""

import numpy as np
import pytest
from asr_pipeline.audio_preprocessor import AudioPreprocessor


def test_audio_normalization_and_dc_offset():
    preprocessor = AudioPreprocessor()
    # Create test signal with DC bias
    raw_signal = np.sin(np.linspace(0, 10 * np.pi, 16000)) + 0.5
    cleaned = preprocessor.remove_dc_offset(raw_signal)

    assert abs(np.mean(cleaned)) < 1e-4

    normalized = preprocessor.peak_normalize(cleaned, target_peak=0.90)
    assert np.max(np.abs(normalized)) == pytest.approx(0.90, abs=1e-3)


def test_linear_resampling():
    preprocessor = AudioPreprocessor(target_sample_rate=16000)
    # 44100 Hz input, 1 second
    orig_sr = 44100
    orig_audio = np.sin(np.linspace(0, 20 * np.pi, orig_sr)).astype(np.float32)

    resampled = preprocessor.resample_linear(orig_audio, orig_sr, 16000)
    assert len(resampled) == 16000


def test_vad_active_and_silent_detection():
    preprocessor = AudioPreprocessor(target_sample_rate=16000, vad_energy_threshold=0.02)

    # Pure silence
    silent_audio = np.zeros(16000, dtype=np.float32)
    mask_silent, ratio_silent = preprocessor.detect_vad_mask(silent_audio)
    assert ratio_silent == 0.0

    # Strong speech-like sine burst
    active_audio = (np.sin(np.linspace(0, 50 * np.pi, 16000)) * 0.5).astype(np.float32)
    mask_active, ratio_active = preprocessor.detect_vad_mask(active_audio)
    assert ratio_active > 0.80


def test_snr_estimation():
    preprocessor = AudioPreprocessor()
    # Signal with distinct high and low energy regions
    audio = np.zeros(16000, dtype=np.float32)
    audio[:12000] = 0.5 * np.sin(np.linspace(0, 20 * np.pi, 12000))
    audio[12000:] = 0.005 * np.random.randn(4000)

    snr = preprocessor.estimate_snr(audio)
    assert snr > 15.0


def test_wav_serialization_roundtrip():
    preprocessor = AudioPreprocessor()
    orig = (np.sin(np.linspace(0, 10 * np.pi, 8000)) * 0.8).astype(np.float32)
    wav_bytes = preprocessor.to_wav_bytes(orig, sample_rate=16000)
    assert len(wav_bytes) > 44  # Valid WAV header

    loaded, sr = preprocessor.load_wav_bytes(wav_bytes)
    assert sr == 16000
    assert len(loaded) == len(orig)
    assert np.max(np.abs(loaded - orig)) < 1e-3
