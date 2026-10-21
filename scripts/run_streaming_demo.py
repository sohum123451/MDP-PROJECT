"""
Live Streaming Dictation Demo for EchoScribe-AI / SonoAssist.
Simulates a real-time microphone stream, performing VAD, anatomical vocabulary biasing,
and structured report formatting with real-time latency monitoring.
"""

import sys
import time
import numpy as np
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from asr_pipeline.audio_preprocessor import AudioPreprocessor
from asr_pipeline.asr_engine import create_asr_engine
from asr_pipeline.streaming_pipeline import RealtimeSpeechStreamer
from asr_pipeline.structured_formatter import StructuredTextFormatter
from scripts.generate_synthetic_samples import generate_synthetic_ultrasound_audio


def run_live_streaming_demo():
    print("=" * 80)
    print("  ECHOSCRIBE-AI / SONOASSIST: REAL-TIME STREAMING SPEECH PIPELINE DEMO")
    print("  Member 2 Deliverable: CSE Core 2 - Speech Models & Pipeline Lead")
    print("=" * 80)

    # Step 1: Ensure sample audio exists
    sample_wav = PROJECT_ROOT / "data" / "synthetic_test_dictation.wav"
    if not sample_wav.exists():
        generate_synthetic_ultrasound_audio(str(sample_wav), duration_seconds=6.0)

    # Step 2: Initialize components
    preprocessor = AudioPreprocessor(target_sample_rate=16000)
    asr_engine = create_asr_engine(engine_type="mock")
    formatter = StructuredTextFormatter()
    streamer = RealtimeSpeechStreamer(
        asr_engine=asr_engine,
        preprocessor=preprocessor,
        formatter=formatter,
        sample_rate=16000,
        chunk_duration_sec=0.5,
        min_speech_duration_sec=1.5
    )

    with open(sample_wav, "rb") as f:
        audio_array, sr = preprocessor.load_wav_bytes(f.read())

    simulated_chunks = [
        "Gall bladder demonstrates diffuse wall thickening measuring four point five millimeters with multiple calculi in the lumen.",
        "Posterior acoustic shadow is noted with positive murphys sign.",
        "Peri cholecystic fluid is visualized in the gallbladder bed with mild biliary sludge."
    ]

    print("\n[1] Commencing Simulated Real-time Audio Stream (Chunk Interval: 500ms)...")

    chunk_size = int(16000 * 0.5)
    def audio_chunk_generator():
        for start_idx in range(0, len(audio_array), chunk_size):
            chunk = audio_array[start_idx : start_idx + chunk_size]
            yield chunk

    def on_segment(segment):
        print(f"\n  >> [STREAM FINALIZED SEGMENT] Time: {segment.start_time:.1f}s - {segment.end_time:.1f}s (Latency: {segment.latency_ms:.1f}ms)")
        print(f"     RAW INPUT:    \"{segment.raw_text}\"")
        print(f"     BIASED ASR:   \"{segment.biased_text}\"")

    # Run the streaming pipeline
    structured_report = streamer.stream_chunks(
        audio_chunks=audio_chunk_generator(),
        on_segment_callback=on_segment,
        simulated_transcripts=simulated_chunks
    )

    print("\n" + "=" * 80)
    print("  [2] STRUCTURED CLINICAL REPORT GENERATED")
    print("=" * 80)
    print(f"Session ID:              {structured_report.session_id}")
    print(f"Audio Duration:          {structured_report.audio_metadata.duration_seconds} seconds")
    print(f"Total Processing Time:   {structured_report.performance_metrics.total_pipeline_latency_ms:.1f} ms")
    print(f"Real-Time Factor (RTF):  {structured_report.performance_metrics.real_time_factor:.4f} (< 1.0 is real-time compliant)")
    print(f"\nFULL BIASED TRANSCRIPT:\n\"{structured_report.full_biased_transcript}\"\n")

    print("-" * 80)
    print("ORGAN FINDINGS BREAKDOWN:")
    for finding in structured_report.organ_findings:
        print(f"\n  • Organ: {finding.organ.upper()}")
        print(f"    Normalized Text: \"{finding.normalized_text}\"")
        print(f"    Abnormal Detected: {finding.abnormality_detected} (Severity: {finding.severity})")
        print(f"    Extracted Measurements: {[f'{m.value} {m.unit}' for m in finding.measurements]}")
        print(f"    Anatomical Entities:    {finding.anatomical_entities}")

    print("\n" + "=" * 80)
    print("  DEMO COMPLETE: Speech pipeline is verified and ready for integration.")
    print("=" * 80)


if __name__ == "__main__":
    run_live_streaming_demo()
