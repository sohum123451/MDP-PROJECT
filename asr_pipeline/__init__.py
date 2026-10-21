"""
EchoScribe-AI / SonoAssist: Anatomical Vocabulary-Biased Speech Recognition Suite.
Member 2 (CSE Core 2) Deliverable.
"""

from asr_pipeline.audio_preprocessor import AudioPreprocessor
from asr_pipeline.phonetic_dictionary import PhoneticDictionary
from asr_pipeline.vocabulary_biasing import VocabularyBiasingEngine
from asr_pipeline.asr_engine import BaseASREngine, MockBiasedASREngine, HuggingFaceWhisperEngine, create_asr_engine
from asr_pipeline.structured_formatter import StructuredTextFormatter
from asr_pipeline.streaming_pipeline import RealtimeSpeechStreamer, StreamingAudioBuffer
from asr_pipeline.session_models import (
    AudioMetadata,
    ASRToken,
    ASRSegment,
    ClinicalMeasurement,
    OrganFinding,
    ASRPerformanceMetrics,
    StructuredUltrasoundDictation
)

__version__ = "1.0.0"
__all__ = [
    "AudioPreprocessor",
    "PhoneticDictionary",
    "VocabularyBiasingEngine",
    "BaseASREngine",
    "MockBiasedASREngine",
    "HuggingFaceWhisperEngine",
    "create_asr_engine",
    "StructuredTextFormatter",
    "RealtimeSpeechStreamer",
    "StreamingAudioBuffer",
    "AudioMetadata",
    "ASRToken",
    "ASRSegment",
    "ClinicalMeasurement",
    "OrganFinding",
    "ASRPerformanceMetrics",
    "StructuredUltrasoundDictation"
]
