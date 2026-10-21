"""
Audio Preprocessing and Voice Activity Detection (VAD) Pipeline.
Standardizes clinical audio inputs to 16kHz mono, applies noise suppression,
normalization, pre-emphasis, and frames active speech bursts.
"""

import numpy as np
import io
import wave
import math
from typing import Tuple, List, Optional
from asr_pipeline.session_models import AudioMetadata


class AudioPreprocessor:
    """
    Robust audio preprocessor for medical clinical dictations.
    Ensures optimal acoustic input for ASR models.
    """

    def __init__(
        self,
        target_sample_rate: int = 16000,
        pre_emphasis_coeff: float = 0.97,
        frame_duration_ms: int = 30,
        vad_energy_threshold: float = 0.015,
        vad_hangover_frames: int = 8,
    ):
        self.target_sample_rate = target_sample_rate
        self.pre_emphasis_coeff = pre_emphasis_coeff
        self.frame_duration_ms = frame_duration_ms
        self.vad_energy_threshold = vad_energy_threshold
        self.vad_hangover_frames = vad_hangover_frames
        self.frame_size = int(self.target_sample_rate * (self.frame_duration_ms / 1000.0))

    def load_wav_bytes(self, wav_bytes: bytes) -> Tuple[np.ndarray, int]:
        """Loads in-memory WAV byte stream into floating-point numpy array [-1.0, 1.0]."""
        with io.BytesIO(wav_bytes) as bio:
            with wave.open(bio, "rb") as wf:
                num_channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                sample_rate = wf.getframerate()
                n_frames = wf.getnframes()
                raw_data = wf.readframes(n_frames)

        if sample_width == 2:
            dtype = np.int16
            max_val = 32768.0
        elif sample_width == 4:
            dtype = np.int32
            max_val = 2147483648.0
        elif sample_width == 1:
            dtype = np.uint8
            # 8-bit unsigned
            audio_np = (np.frombuffer(raw_data, dtype=dtype).astype(np.float32) - 128.0) / 128.0
            if num_channels > 1:
                audio_np = audio_np.reshape(-1, num_channels).mean(axis=1)
            return audio_np, sample_rate
        else:
            raise ValueError(f"Unsupported WAV sample width: {sample_width} bytes")

        audio_np = np.frombuffer(raw_data, dtype=dtype).astype(np.float32) / max_val
        if num_channels > 1:
            audio_np = audio_np.reshape(-1, num_channels).mean(axis=1)

        return audio_np, sample_rate

    def to_wav_bytes(self, audio: np.ndarray, sample_rate: Optional[int] = None) -> bytes:
        """Converts float numpy array [-1.0, 1.0] back to 16-bit PCM WAV bytes."""
        sr = sample_rate or self.target_sample_rate
        clipped = np.clip(audio, -1.0, 1.0)
        pcm16 = (clipped * 32767.0).astype(np.int16)

        out_io = io.BytesIO()
        with wave.open(out_io, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(pcm16.tobytes())

        return out_io.getvalue()

    def resample_linear(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """High-efficiency linear interpolation resampling without external heavy dependencies."""
        if orig_sr == target_sr or len(audio) == 0:
            return audio

        num_orig = len(audio)
        num_target = int(math.ceil(num_orig * (target_sr / orig_sr)))
        orig_indices = np.linspace(0, num_orig - 1, num_orig)
        target_indices = np.linspace(0, num_orig - 1, num_target)
        resampled = np.interp(target_indices, orig_indices, audio)
        return resampled.astype(np.float32)

    def remove_dc_offset(self, audio: np.ndarray) -> np.ndarray:
        """Removes DC bias from microphone electrical signals."""
        if len(audio) == 0:
            return audio
        return audio - np.mean(audio)

    def peak_normalize(self, audio: np.ndarray, target_peak: float = 0.95) -> np.ndarray:
        """Peak-normalizes the signal to prevent clipping while maximizing dynamic range."""
        max_abs = np.max(np.abs(audio)) if len(audio) > 0 else 0.0
        if max_abs > 1e-6:
            return audio * (target_peak / max_abs)
        return audio

    def apply_pre_emphasis(self, audio: np.ndarray) -> np.ndarray:
        """
        Applies pre-emphasis filter y[n] = x[n] - alpha * x[n-1]
        Boosts high-frequency anatomical consonant sounds (s, sh, th, k).
        """
        if len(audio) < 2:
            return audio
        return np.append(audio[0], audio[1:] - self.pre_emphasis_coeff * audio[:-1])

    def estimate_snr(self, audio: np.ndarray) -> float:
        """
        Estimates the Signal-to-Noise Ratio (dB) by comparing upper 90th percentile
        energy frames against lower 10th percentile background noise frames.
        """
        if len(audio) < self.frame_size:
            return 20.0  # Default nominal SNR

        n_frames = len(audio) // self.frame_size
        frame_energies = [
            np.mean(audio[i * self.frame_size : (i + 1) * self.frame_size] ** 2)
            for i in range(n_frames)
        ]
        if not frame_energies:
            return 20.0

        sorted_energies = np.sort(frame_energies)
        noise_energy = np.mean(sorted_energies[: max(1, int(0.15 * n_frames))]) + 1e-10
        signal_energy = np.mean(sorted_energies[int(0.80 * n_frames) :]) + 1e-10

        snr = 10.0 * np.log10(signal_energy / noise_energy)
        return float(np.clip(snr, 0.0, 60.0))

    def detect_vad_mask(self, audio: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Energy and zero-crossing rate Voice Activity Detection (VAD).
        Returns a boolean frame mask and speech ratio.
        """
        if len(audio) == 0:
            return np.array([], dtype=bool), 0.0

        num_frames = len(audio) // self.frame_size
        if num_frames == 0:
            return np.array([True], dtype=bool), 1.0

        is_speech = np.zeros(num_frames, dtype=bool)

        for i in range(num_frames):
            frame = audio[i * self.frame_size : (i + 1) * self.frame_size]
            rms = np.sqrt(np.mean(frame ** 2))
            if rms >= self.vad_energy_threshold:
                is_speech[i] = True

        # Apply hangover smoothing (prevent cutting off speech in inter-syllable pauses)
        smoothed = np.copy(is_speech)
        hangover = 0
        for i in range(num_frames):
            if is_speech[i]:
                hangover = self.vad_hangover_frames
                smoothed[i] = True
            elif hangover > 0:
                hangover -= 1
                smoothed[i] = True

        speech_ratio = float(np.mean(smoothed)) if len(smoothed) > 0 else 0.0
        return smoothed, speech_ratio

    def preprocess(
        self,
        audio: np.ndarray,
        sample_rate: int,
        apply_filter: bool = True
    ) -> Tuple[np.ndarray, AudioMetadata]:
        """
        Full end-to-end preprocessing pipeline:
        1. Resampling to 16kHz
        2. DC offset removal
        3. Peak normalization
        4. Optional pre-emphasis
        5. VAD analysis and SNR estimation
        """
        # 1. Resample if necessary
        if sample_rate != self.target_sample_rate:
            audio = self.resample_linear(audio, sample_rate, self.target_sample_rate)

        # 2. DC offset removal
        audio = self.remove_dc_offset(audio)

        # 3. Peak normalize
        audio = self.peak_normalize(audio)

        # 4. Metrics estimation
        snr_db = self.estimate_snr(audio)
        _, speech_ratio = self.detect_vad_mask(audio)

        # 5. Pre-emphasis
        if apply_filter:
            processed_audio = self.apply_pre_emphasis(audio)
        else:
            processed_audio = audio

        duration_sec = len(processed_audio) / float(self.target_sample_rate)
        metadata = AudioMetadata(
            sample_rate=self.target_sample_rate,
            channels=1,
            bit_depth=16,
            duration_seconds=round(duration_sec, 3),
            snr_db=round(snr_db, 2),
            vad_speech_ratio=round(speech_ratio, 3)
        )

        return processed_audio, metadata
