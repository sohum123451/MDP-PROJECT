"""
Unit Tests for Streaming Audio Buffer and Real-Time Speech Streamer.
"""

import numpy as np
from asr_pipeline.streaming_pipeline import StreamingAudioBuffer, RealtimeSpeechStreamer
from asr_pipeline.asr_engine import MockBiasedASREngine


def test_streaming_buffer_append_and_cap():
    buffer = StreamingAudioBuffer(sample_rate=16000, max_duration_sec=2.0)
    assert buffer.duration_seconds == 0.0

    chunk = np.ones(16000, dtype=np.float32)  # 1 second
    buffer.append(chunk)
    assert buffer.duration_seconds == 1.0

    buffer.append(chunk)
    assert buffer.duration_seconds == 2.0

    # Appending more should roll over and cap at max_samples (2.0s)
    buffer.append(chunk)
    assert buffer.duration_seconds == 2.0

    buffer.clear()
    assert buffer.duration_seconds == 0.0


def test_realtime_speech_streamer_execution():
    asr = MockBiasedASREngine()
    streamer = RealtimeSpeechStreamer(
        asr_engine=asr,
        sample_rate=16000,
        chunk_duration_sec=0.5,
        min_speech_duration_sec=1.0
    )

    # 4 chunks of 0.5s = 2.0s audio
    chunks = [
        np.sin(np.linspace(0, 20 * np.pi, 8000)).astype(np.float32) * 0.4
        for _ in range(4)
    ]

    emitted_segments = []
    def on_seg(seg):
        emitted_segments.append(seg)

    report = streamer.stream_chunks(
        audio_chunks=iter(chunks),
        on_segment_callback=on_seg,
        simulated_transcripts=["The liver is normal in echotexture."]
    )

    assert len(emitted_segments) >= 1
    assert report.performance_metrics.total_pipeline_latency_ms > 0
    assert report.performance_metrics.real_time_factor < 1.0
    assert len(report.organ_findings) >= 1
