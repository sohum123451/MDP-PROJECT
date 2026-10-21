"""
Unified Session Data Schemas for EchoScribe-AI / SonoAssist.
Provides strict Pydantic data contracts between CSE Core 1 (Capture),
CSE Core 2 (Speech Models), CSE DS (Harness), and IT (UI Screen).
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
import time
import uuid


class AudioMetadata(BaseModel):
    """Metadata describing the input audio capture characteristics."""
    sample_rate: int = Field(default=16000, description="Sampling rate in Hz (target: 16kHz)")
    channels: int = Field(default=1, description="Number of audio channels (1=mono)")
    bit_depth: int = Field(default=16, description="Bit depth per sample")
    duration_seconds: float = Field(default=0.0, description="Duration in seconds")
    snr_db: Optional[float] = Field(default=None, description="Estimated Signal-to-Noise Ratio (dB)")
    vad_speech_ratio: Optional[float] = Field(default=None, description="Ratio of active speech frames detected")


class ASRToken(BaseModel):
    """Detailed token information with timing and anatomical relevance."""
    text: str
    start_time: float
    end_time: float
    confidence: float = 1.0
    is_anatomical_term: bool = False
    phonetic_correction_applied: bool = False
    original_text: Optional[str] = None


class ASRSegment(BaseModel):
    """Segment produced during real-time speech streaming."""
    segment_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    start_time: float
    end_time: float
    raw_text: str
    biased_text: str
    is_final: bool = False
    confidence: float = 0.95
    tokens: List[ASRToken] = Field(default_factory=list)
    latency_ms: float = 0.0


class ClinicalMeasurement(BaseModel):
    """Extracted numeric measurement with unit and anatomical context."""
    parameter: str
    value: float
    unit: str
    raw_mention: str
    confidence: float = 1.0


class OrganFinding(BaseModel):
    """Structured clinical finding segmented by anatomical organ."""
    organ: Literal[
        "liver",
        "gallbladder",
        "pancreas",
        "spleen",
        "right_kidney",
        "left_kidney",
        "kidneys",
        "aorta",
        "peritoneum",
        "general"
    ]
    raw_dictation: str
    normalized_text: str
    abnormality_detected: bool = False
    severity: Literal["normal", "mild", "moderate", "severe", "indeterminate"] = "normal"
    measurements: List[ClinicalMeasurement] = Field(default_factory=list)
    anatomical_entities: List[str] = Field(default_factory=list)
    echogenicity_features: List[str] = Field(default_factory=list)


class ASRPerformanceMetrics(BaseModel):
    """Latency and processing efficiency metrics for the speech pipeline."""
    preprocessing_latency_ms: float = 0.0
    asr_inference_latency_ms: float = 0.0
    formatting_latency_ms: float = 0.0
    total_pipeline_latency_ms: float = 0.0
    real_time_factor: float = 0.0  # processing_time / audio_duration (< 1.0 is real-time)


class StructuredUltrasoundDictation(BaseModel):
    """Comprehensive structured output payload returned by the Speech Pipeline."""
    session_id: str = Field(default_factory=lambda: f"SESS_{int(time.time())}")
    timestamp: float = Field(default_factory=time.time)
    audio_metadata: AudioMetadata = Field(default_factory=AudioMetadata)
    full_raw_transcript: str = ""
    full_biased_transcript: str = ""
    segments: List[ASRSegment] = Field(default_factory=list)
    organ_findings: List[OrganFinding] = Field(default_factory=list)
    performance_metrics: ASRPerformanceMetrics = Field(default_factory=ASRPerformanceMetrics)
    metadata: Dict[str, Any] = Field(default_factory=dict)
