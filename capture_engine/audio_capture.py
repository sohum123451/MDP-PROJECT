"""
Synchronous Audio Capture Pipeline for Ultrasound Dictations.
Member 1 (Joel - CSE Core 1 Deliverable).
Records audio in lockstep with video keyframe capture, maintaining millisecond
synchronization with the master session clock.
"""

import time
import io
import wave
import numpy as np
from typing import Optional, Tuple, Dict, Any
from pathlib import Path


class SynchronousAudioRecorder:
    """
    Audio recording pipeline for clinical ultrasound examination dictations.
    Maintains synchronous alignment with video frame grabber.
    """

    def __init__(self, sample_rate: int = 16000, output_dir: Optional[str] = None):
        self.sample_rate = sample_rate
        self.output_dir = Path(output_dir or "data/captured_audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.is_recording = False
        self.start_time: Optional[float] = None
        self.audio_buffer: np.ndarray = np.zeros(0, dtype=np.float32)

    def start_recording(self, session_clock_time: Optional[float] = None) -> float:
        """Starts recording aligned with the master session clock."""
        self.start_time = session_clock_time or time.time()
        self.is_recording = True
        self.audio_buffer = np.zeros(0, dtype=np.float32)
        return self.start_time

    def append_chunk(self, chunk: np.ndarray) -> None:
        """Ingests live PCM float audio samples [-1.0, 1.0]."""
        if not self.is_recording:
            return
        self.audio_buffer = np.append(self.audio_buffer, chunk)

    def stop_recording(self, session_id: str = "SESSION") -> Tuple[str, Dict[str, Any]]:
        """
        Finalizes recording, writes standard 16kHz mono PCM WAV file,
        and returns the file path alongside audio capture telemetry.
        """
        self.is_recording = False
        duration = len(self.audio_buffer) / float(self.sample_rate)

        out_path = self.output_dir / f"{session_id}_dictation.wav"

        # Clip and convert to 16-bit PCM
        clipped = np.clip(self.audio_buffer, -1.0, 1.0)
        pcm16 = (clipped * 32767.0).astype(np.int16)

        with wave.open(str(out_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(pcm16.tobytes())

        clipping_count = int(np.sum(np.abs(self.audio_buffer) >= 0.99))
        clipping_rate = float(clipping_count) / max(1, len(self.audio_buffer))

        telemetry = {
            "duration_seconds": round(duration, 3),
            "sample_rate": self.sample_rate,
            "channels": 1,
            "total_samples": len(self.audio_buffer),
            "clipping_percentage": round(clipping_rate * 100.0, 3),
            "file_path": str(out_path)
        }

        return str(out_path), telemetry
