"""
Unit Tests for Capture Engine & Lead Systems Integrator (Joel - CSE Core 1).
"""

import numpy as np
import pytest
from capture_engine.frame_grabber import UltrasoundFrameGrabber
from capture_engine.audio_capture import SynchronousAudioRecorder
from capture_engine.session_aggregator import UnifiedSessionAggregator


def test_frame_grabber_trigger():
    grabber = UltrasoundFrameGrabber(output_dir="data/test_keyframes")
    grabber.start_session()

    meta, path = grabber.trigger_keyframe_capture(
        target_organ="gallbladder",
        trigger_source="hardware_foot_pedal"
    )

    assert meta.target_organ == "gallbladder"
    assert meta.trigger_source == "hardware_foot_pedal"
    assert meta.timestamp_offset_ms >= 0.0
    assert len(grabber.get_session_summary()) == 1


def test_audio_recorder_synchronous_capture():
    recorder = SynchronousAudioRecorder(sample_rate=16000, output_dir="data/test_audio")
    recorder.start_recording()

    # Feed 0.5s audio chunk
    chunk = (np.sin(np.linspace(0, 10 * np.pi, 8000)) * 0.5).astype(np.float32)
    recorder.append_chunk(chunk)

    wav_path, telemetry = recorder.stop_recording(session_id="TEST_001")
    assert telemetry["total_samples"] == 8000
    assert telemetry["duration_seconds"] == 0.5
    assert telemetry["clipping_percentage"] == 0.0


def test_unified_session_aggregation():
    aggregator = UnifiedSessionAggregator(session_id="TEST_SESS_99")
    aggregator.attach_captured_frames([{"frame_id": "F1", "target_organ": "liver"}])
    aggregator.attach_audio_telemetry({"duration_seconds": 4.5, "sample_rate": 16000})
    aggregator.attach_speech_stream(
        raw_transcript="The liver has steatosis",
        biased_transcript="The liver has steatosis",
        segments=[1]
    )
    aggregator.attach_structured_report(
        organ_findings=[{"organ": "liver", "abnormal": True}],
        impression="Moderate hepatic steatosis."
    )

    payload = aggregator.compile_unified_session()
    assert payload["session_id"] == "TEST_SESS_99"
    assert len(payload["captured_frames"]) == 1
    assert payload["structured_report"]["overall_impression"] == "Moderate hepatic steatosis."
