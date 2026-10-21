# Team Integration Guide: Speech Models & Pipeline (Member 2)
**Project:** EchoScribe-AI / SonoAssist  
**Role:** Member 2 (CSE Core 2) — Speech Models & Pipeline Lead  

This document explains how each team member integrates their deliverables with the Member 2 Speech Pipeline.

---

## 1. Member 1 (CSE Core 1) — Frame Grabber & Synchronous Capture Integration

**Member 1 Deliverable:** Frame grabber module & button-press trigger + mic audio capture.

### Integration Interface:
When the radiologist speaks into the microphone during frame capture, Member 1 feeds either in-memory WAV bytes or a raw audio NumPy chunk directly into Member 2's `AudioPreprocessor` or `RealtimeSpeechStreamer`:

```python
from asr_pipeline.audio_preprocessor import AudioPreprocessor
from asr_pipeline.streaming_pipeline import RealtimeSpeechStreamer

preprocessor = AudioPreprocessor(target_sample_rate=16000)

# Option A: Ingest captured WAV file from Member 1's audio recorder
audio_np, sample_rate = preprocessor.load_wav_bytes(captured_audio_bytes)
cleaned_audio, audio_metadata = preprocessor.preprocess(audio_np, sample_rate)

# Option B: Live streaming mic chunks directly into RealtimeSpeechStreamer
streamer = RealtimeSpeechStreamer()
structured_report = streamer.stream_chunks(member_1_audio_generator)
```

The returned `audio_metadata` and `structured_report` adhere strictly to the shared `session_models.py` schema.

---

## 2. Member 3 (CSE DS) — LLM Comparison Harness Integration

**Member 3 Deliverable:** LLM comparison harness & quantitative dataset evaluations (including abnormal-only slice).

### Integration Interface:
Member 3 takes the output of Member 2 (`StructuredUltrasoundDictation.organ_findings` and `full_biased_transcript`) as the prompt input to test open-weight LLMs (e.g. LLaMA-3, Mistral, Gemma):

```python
from asr_pipeline.session_models import StructuredUltrasoundDictation

def prompt_from_asr(report: StructuredUltrasoundDictation) -> str:
    organ_context = "\n".join([
        f"- {finding.organ.upper()}: {finding.normalized_text} (Abnormal: {finding.abnormality_detected})"
        for finding in report.organ_findings
    ])
    return f"""You are a specialized Radiologist assistant.
Convert these ultrasound dictation findings into a formal ACR-compliant report:

DICTATION FINDINGS:
{organ_context}

FINAL IMPRESSION & REPORT:"""
```

Member 3 can also use `benchmarks/evaluate_biased_asr.py` as an established reference for computing WER and clinical semantic metrics.

---

## 3. Member 4 (IT) — Review & Correct UI Screen Integration

**Member 4 Deliverable:** Radiologist Web Review UI, Audit Trail, and on-prem deployment.

### Integration Interface:
Member 2 provides full JSON serialization via Pydantic:

```python
# Convert structured ultrasound dictation to JSON for Web UI / REST / WebSocket
json_payload = structured_report.model_dump_json(indent=2)
```

In the UI:
- `structured_report.segments`: Display real-time streaming speech bubbles as words are spoken.
- `structured_report.organ_findings`: Populate individual organ review accordions (Liver, Gallbladder, Kidneys, Spleen, etc.).
- `structured_report.performance_metrics.real_time_factor`: Display live system latency telemetry badge.

---

## 4. Member 5 (Health Science) — Clinical Taxonomy & Validation Integration

**Member 5 Deliverable:** Abdominal ultrasound report taxonomy, clinical error severity rubric, and ground-truth validation.

### Integration Interface:
The anatomical dictionary is externalized in `data/abdominal_ultrasound_lexicon.json` and `data/phonetic_corrections.json`.  
Member 5 can directly edit or add new ultrasound jargon, acoustic homophones, or anatomical landmarks without modifying Python code!
