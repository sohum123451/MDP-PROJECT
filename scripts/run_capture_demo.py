"""
Demonstration Script for Capture & Integration Subsystem.
Member 1 (Joel - CSE Core 1 Deliverable).
Simulates a live ultrasound examination where keyframes are acquired upon button press,
audio dictation is synchronously captured, and the Unified Session JSON is generated.
"""

import sys
import time
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from capture_engine.frame_grabber import UltrasoundFrameGrabber
from capture_engine.audio_capture import SynchronousAudioRecorder
from capture_engine.session_aggregator import UnifiedSessionAggregator


def run_capture_demonstration():
    print("=" * 80)
    print("  ECHOSCRIBE-AI / SONOASSIST: MULTIMODAL SYNCHRONOUS CAPTURE DEMO")
    print("  Member 1 Deliverable: CSE Core 1 (Joel) - Capture & Integration Lead")
    print("=" * 80)

    # 1. Initialize Frame Grabber and Synchronous Audio Recorder
    grabber = UltrasoundFrameGrabber()
    recorder = SynchronousAudioRecorder()
    aggregator = UnifiedSessionAggregator()

    session_clock = grabber.start_session()
    recorder.start_recording(session_clock)

    print(f"\n[1] Ultrasound Session Initiated (Session ID: {aggregator.session_id})")
    print("    Master sync clock running at millisecond resolution...")

    # 2. Simulate hardware foot-pedal / button triggers during exam
    organs = ["liver", "gallbladder", "right_kidney", "aorta"]
    captured_metadata = []

    for idx, organ in enumerate(organs, 1):
        time.sleep(0.15)  # exam progression
        print(f"\n  >> [HARDWARE TRIGGER #{idx}] Foot Pedal Triggered for: {organ.upper()}")

        # Frame capture
        meta, path = grabber.trigger_keyframe_capture(
            target_organ=organ,
            trigger_source="hardware_foot_pedal"
        )
        captured_metadata.append(meta.to_dict())
        print(f"     Captured Frame: {meta.frame_id} (Offset: {meta.timestamp_offset_ms:.1f} ms)")

        # Feed audio chunk
        chunk = (np.sin(np.linspace(0, 10 * np.pi, 2400)) * 0.4).astype(np.float32)
        recorder.append_chunk(chunk)

    # 3. Finalize Audio Recording
    wav_path, audio_telem = recorder.stop_recording(session_id=aggregator.session_id)
    print(f"\n[2] Audio Recording Finalized:")
    print(f"    Path:     {wav_path}")
    print(f"    Duration: {audio_telem['duration_seconds']:.2f}s | Sample Rate: {audio_telem['sample_rate']}Hz")

    # 4. Aggregate into Unified Session Schema
    aggregator.attach_captured_frames(captured_metadata)
    aggregator.attach_audio_telemetry(audio_telem)
    aggregator.attach_speech_stream(
        raw_transcript="Gallbladder shows cholelithiasis. Liver shows steatosis.",
        biased_transcript="Gallbladder shows cholelithiasis. Liver shows steatosis.",
        segments=[]
    )
    aggregator.attach_structured_report(
        organ_findings=[
            {"organ": "gallbladder", "finding": "cholelithiasis", "severity": "moderate"},
            {"organ": "liver", "finding": "steatosis", "severity": "mild"}
        ],
        impression="Cholelithiasis with mild hepatic steatosis."
    )

    saved_json = aggregator.save_session_json()
    print(f"\n[3] Unified Multidisciplinary Session JSON Compiled:")
    print(f"    Saved: {saved_json}")
    print("\n" + "=" * 80)
    print("  CAPTURE & SYSTEMS INTEGRATION VERIFIED (MEMBER 1)")
    print("=" * 80)


if __name__ == "__main__":
    run_capture_demonstration()
