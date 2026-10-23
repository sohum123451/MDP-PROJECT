"""
Capture Engine and Lead Systems Integration Package.
Member 1 (Joel - CSE Core 1 Deliverable).
"""

from capture_engine.frame_grabber import UltrasoundFrameGrabber, KeyframeMetadata
from capture_engine.audio_capture import SynchronousAudioRecorder
from capture_engine.session_aggregator import UnifiedSessionAggregator

__all__ = [
    "UltrasoundFrameGrabber",
    "KeyframeMetadata",
    "SynchronousAudioRecorder",
    "UnifiedSessionAggregator"
]
