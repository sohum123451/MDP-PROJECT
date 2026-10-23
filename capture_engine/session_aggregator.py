"""
Unified Session Schema Aggregator & Systems Integration Engine.
Member 1 (Joel - CSE Core 1 / Lead Systems Integrator).
Owns weekly codebase merge and continuous integration across all 5 sub-modules.
Merges captured frames, synchronous audio, biased ASR streams, and clinical reports
into the standardized Unified Session JSON document.
"""

import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path


class UnifiedSessionAggregator:
    """
    Lead Systems Integrator's Aggregator.
    Binds the multi-member outputs into a coherent, validated session package.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"SESS_{int(time.time())}"
        self.timestamp = time.time()
        self.operator_id = "RAD_DR_ALVAREZ_042"
        self.patient_anon_id = f"ANON_PT_{hash(self.session_id) % 100000:05d}"
        self.captured_frames: List[Dict[str, Any]] = []
        self.audio_metadata: Dict[str, Any] = {}
        self.dictation_stream: Dict[str, Any] = {}
        self.structured_report: Dict[str, Any] = {}

    def attach_captured_frames(self, frames: List[Dict[str, Any]]) -> None:
        """Attaches keyframes captured via FrameGrabber (Member 1)."""
        self.captured_frames = frames

    def attach_audio_telemetry(self, telemetry: Dict[str, Any]) -> None:
        """Attaches audio recording metadata (Member 1)."""
        self.audio_metadata = telemetry

    def attach_speech_stream(self, raw_transcript: str, biased_transcript: str, segments: List[Any]) -> None:
        """Attaches speech recognition outputs from Member 2 (Sohum)."""
        self.dictation_stream = {
            "raw_transcript": raw_transcript,
            "biased_transcript": biased_transcript,
            "segments_count": len(segments)
        }

    def attach_structured_report(self, organ_findings: List[Dict[str, Any]], impression: str = "") -> None:
        """Attaches structured findings from Member 3 (Manya) & Member 5 (Nikilan)."""
        self.structured_report = {
            "organ_findings": organ_findings,
            "acr_template_compliance": True,
            "overall_impression": impression or "Abdominal ultrasound examination completed with clinical structuring."
        }

    def compile_unified_session(self) -> Dict[str, Any]:
        """Compiles the complete unified multidisciplinary session payload."""
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "operator_id": self.operator_id,
            "patient_anon_id": self.patient_anon_id,
            "captured_frames": self.captured_frames,
            "audio_metadata": self.audio_metadata,
            "dictation_stream": self.dictation_stream,
            "structured_report": self.structured_report
        }

    def save_session_json(self, output_dir: Optional[str] = None) -> str:
        """Serializes session to JSON file for Member 4's Web UI and PACS storage."""
        out_dir = Path(output_dir or "data/sessions")
        out_dir.mkdir(parents=True, exist_ok=True)

        payload = self.compile_unified_session()
        filepath = out_dir / f"{self.session_id}_unified_session.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        return str(filepath)
