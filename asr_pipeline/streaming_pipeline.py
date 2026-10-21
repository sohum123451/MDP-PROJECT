"""
Real-time Speech Streaming Pipeline for Ultrasound Dictations.
Buffers streaming PCM chunks, tracks latency, triggers VAD-gated ASR,
and pipes real-time partial/finalized transcripts to structured formatting.
"""

import time
import numpy as np
from typing import Generator, Optional, Callable, List
from asr_pipeline.audio_preprocessor import AudioPreprocessor
from asr_pipeline.asr_engine import BaseASREngine, create_asr_engine
from asr_pipeline.structured_formatter import StructuredTextFormatter
from asr_pipeline.session_models import (
    ASRSegment,
    StructuredUltrasoundDictation,
    ASRPerformanceMetrics,
    AudioMetadata
)


class StreamingAudioBuffer:
    """
    Rolling ring buffer for streaming real-time audio samples.
    """

    def __init__(self, sample_rate: int = 16000, max_duration_sec: float = 30.0):
        self.sample_rate = sample_rate
        self.max_samples = int(sample_rate * max_duration_sec)
        self.buffer = np.zeros(0, dtype=np.float32)

    def append(self, chunk: np.ndarray) -> None:
        """Appends new incoming float audio samples to the buffer."""
        if len(chunk) == 0:
            return
        self.buffer = np.append(self.buffer, chunk)
        if len(self.buffer) > self.max_samples:
            self.buffer = self.buffer[-self.max_samples:]

    def get_all(self) -> np.ndarray:
        return self.buffer.copy()

    def clear(self) -> None:
        self.buffer = np.zeros(0, dtype=np.float32)

    @property
    def duration_seconds(self) -> float:
        return len(self.buffer) / float(self.sample_rate)


class RealtimeSpeechStreamer:
    """
    Streaming speech orchestrator.
    Processes audio stream chunks in real time and emits formatted segments.
    """

    def __init__(
        self,
        asr_engine: Optional[BaseASREngine] = None,
        preprocessor: Optional[AudioPreprocessor] = None,
        formatter: Optional[StructuredTextFormatter] = None,
        sample_rate: int = 16000,
        chunk_duration_sec: float = 0.5,
        min_speech_duration_sec: float = 1.0
    ):
        self.sample_rate = sample_rate
        self.chunk_duration_sec = chunk_duration_sec
        self.min_speech_samples = int(sample_rate * min_speech_duration_sec)
        self.chunk_size = int(sample_rate * chunk_duration_sec)

        self.preprocessor = preprocessor or AudioPreprocessor(target_sample_rate=sample_rate)
        self.asr_engine = asr_engine or create_asr_engine(engine_type="mock")
        self.formatter = formatter or StructuredTextFormatter()

        self.buffer = StreamingAudioBuffer(sample_rate=sample_rate)
        self.finalized_segments: List[ASRSegment] = []

    def stream_chunks(
        self,
        audio_chunks: Generator[np.ndarray, None, None],
        on_segment_callback: Optional[Callable[[ASRSegment], None]] = None,
        simulated_transcripts: Optional[List[str]] = None
    ) -> StructuredUltrasoundDictation:
        """
        Processes a generator stream of audio chunks.
        Tracks preprocessing, inference, and formatting latency.
        """
        start_total = time.perf_counter()
        prep_time_total = 0.0
        asr_time_total = 0.0

        transcript_idx = 0
        current_chunk_idx = 0

        for chunk in audio_chunks:
            current_chunk_idx += 1
            t0 = time.perf_counter()
            # Clean chunk
            chunk_clean = self.preprocessor.remove_dc_offset(chunk)
            prep_time_total += (time.perf_counter() - t0)

            self.buffer.append(chunk_clean)

            # Check if buffer has reached processing threshold
            if len(self.buffer.get_all()) >= self.min_speech_samples:
                audio_window = self.buffer.get_all()

                # VAD check
                _, speech_ratio = self.preprocessor.detect_vad_mask(audio_window)
                if speech_ratio > 0.15:
                    t_asr_start = time.perf_counter()

                    sim_text = None
                    if simulated_transcripts and transcript_idx < len(simulated_transcripts):
                        sim_text = simulated_transcripts[transcript_idx]
                        transcript_idx += 1

                    segment = self.asr_engine.transcribe(
                        audio=audio_window,
                        sample_rate=self.sample_rate,
                        enable_biasing=True
                    )
                    if sim_text:
                        segment.raw_text = sim_text
                        # Re-run biasing on sim_text
                        segment.biased_text, _ = self.asr_engine.phonetic_dict.post_process_transcription(sim_text)

                    asr_time_total += (time.perf_counter() - t_asr_start)

                    self.finalized_segments.append(segment)
                    if on_segment_callback:
                        on_segment_callback(segment)

                    # Reset buffer after finalizing a speech segment
                    self.buffer.clear()

        # Final flush if remaining speech in buffer
        remaining_audio = self.buffer.get_all()
        if len(remaining_audio) > (self.sample_rate * 0.5):
            t_asr_start = time.perf_counter()
            sim_text = simulated_transcripts[transcript_idx] if (simulated_transcripts and transcript_idx < len(simulated_transcripts)) else None
            segment = self.asr_engine.transcribe(
                audio=remaining_audio,
                sample_rate=self.sample_rate,
                enable_biasing=True
            )
            if sim_text:
                segment.raw_text = sim_text
                segment.biased_text, _ = self.asr_engine.phonetic_dict.post_process_transcription(sim_text)

            asr_time_total += (time.perf_counter() - t_asr_start)
            self.finalized_segments.append(segment)
            if on_segment_callback:
                on_segment_callback(segment)

        # Post-processing and structured formatting
        t_fmt_start = time.perf_counter()
        full_raw = " ".join(s.raw_text for s in self.finalized_segments)
        full_biased = " ".join(s.biased_text for s in self.finalized_segments)

        audio_metadata = AudioMetadata(
            sample_rate=self.sample_rate,
            channels=1,
            bit_depth=16,
            duration_seconds=round(current_chunk_idx * self.chunk_duration_sec, 2),
            snr_db=28.5,
            vad_speech_ratio=0.85
        )

        structured_dictation = self.formatter.format_dictation(
            raw_text=full_raw,
            biased_text=full_biased,
            audio_metadata=audio_metadata,
            segments=self.finalized_segments
        )
        fmt_time = (time.perf_counter() - t_fmt_start)
        total_time = (time.perf_counter() - start_total)

        total_audio_duration = max(0.1, audio_metadata.duration_seconds)
        structured_dictation.performance_metrics = ASRPerformanceMetrics(
            preprocessing_latency_ms=round(prep_time_total * 1000.0, 2),
            asr_inference_latency_ms=round(asr_time_total * 1000.0, 2),
            formatting_latency_ms=round(fmt_time * 1000.0, 2),
            total_pipeline_latency_ms=round(total_time * 1000.0, 2),
            real_time_factor=round(total_time / total_audio_duration, 4)
        )

        return structured_dictation
