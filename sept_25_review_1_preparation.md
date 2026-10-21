# Review-I Preparation Package: BAXXX191 Basic Multidisciplinary Project
**Target Review Date:** On or before 25th September 2026  
**Weightage:** 5 Marks  
**Mandatory Outcomes (per Rubric):** Title of the Project, Deep Understanding of Problem Statement, Objectives, and Scope.

---

## 1. Project Title Options

Choose the title option that best matches your team's preferred angle for the panel:

### Category A: Clinical & Technical Precision (Recommended)
1. **EchoScribe-AI: Multimodal Frame Capture, Vocabulary-Biased Speech Recognition, and LLM-Driven Abdominal Ultrasound Reporting**
2. **SonoAssist: Real-Time Multimodal Data Integration and LLM Structuring for Abdominal Ultrasound Documentation**
3. **Anatomically Biased Speech-to-Text and LLM-Assisted Workflow Integration for Abdominal Ultrasound**

### Category B: Data Science & AI Systems Focus
4. **End-to-End Multimodal Ultrasound Reporting Platform: From Live Capture and Biased ASR to Clinical Evaluation**
5. **Data-Driven Ultrasound Documentation: Vocabulary-Biased ASR and LLM Benchmark Harness for Clinical Workflows**

### Category C: High-Impact & Concise
6. **SonoScribe AI: Real-Time Speech and Image Structuring for Abdominal Ultrasound**
7. **OmniReport: Multimodal AI-Assisted Clinical Documentation for Abdominal Imaging**

---

## 2. Executive Summary & Problem Statement

### Clinical Background & Pain Points
Abdominal ultrasound examinations require Sonographers and Radiologists to simultaneously perform transducer manipulation, image acquisition, and verbal annotation of complex anatomical findings (e.g., liver echogenicity, gallbladder wall thickness, renal calculus dimensions). 

- **Cognitive & Physical Burden:** Radiologists spend up to 40% of their session duration manually transcribing dictated notes or typing reports into EHR/PACS systems post-examination.
- **Terminology Errors in Standard ASR:** Off-the-shelf Speech-to-Text (ASR) engines frequently misclassify anatomical jargon (e.g., confusing "hyperechoic lesion" with generic terms or misinterpreting measurement values).
- **Fragmented Workflows:** Image frame capture and audio dictations are disconnected, requiring manual matching of keyframes to written report sections.

### Problem Statement
Existing ultrasound reporting relies on fragmented manual workflows that introduce high transcription latency, potential medical record inaccuracies due to domain-unaware ASR models, and lack of standardized evaluation metrics. There is a critical need for an integrated on-premises system that synchronously captures ultrasound frames and audio, transcribes clinical dictations with anatomical vocabulary biasing, evaluates LLM summarization quality using rigorous data science benchmarks, and provides a secure, audited human-in-the-loop review interface.

---

## 3. Project Objectives & Scope

### Project Objectives
1. **Multimodal Synchronous Capture (CSE Core 1):** Build a frame-grabber and audio capture engine to record high-resolution keyframes (via hardware button/hotkey) alongside audio dictations with unified session schema management.
2. **Anatomical ASR Engine (CSE Core 2):** Fine-tune and bias an ASR engine with specialized abdominal ultrasound anatomical vocabulary to achieve low Word Error Rate (WER) on complex clinical terms.
3. **LLM Harness & Data Benchmarking (CSE DS):** Build an LLM comparison harness, curate specialized dataset splits (including an abnormal-only evaluation slice), and run quantitative evaluations (WER, ROUGE, clinical similarity metrics).
4. **Human-in-the-Loop Clinical UI (IT):** Develop an on-premise review-and-correct web interface featuring edit logging, role-based access control (RBAC), and latency tracking.
5. **Clinical Taxonomy & Validation (Health Science):** Establish an abdominal ultrasound report taxonomy, clinical error severity rubric, and ground-truth annotated dataset guided by clinical leadership.

### Project Scope
* **In-Scope:**
  * Modality: Abdominal Ultrasound (liver, gallbladder, spleen, pancreas, kidneys, aorta).
  * System Architecture: On-premise deployment, local audio/frame processing, LLM comparison harness.
  * Human Interaction: Radiologist review-and-correct interface with change tracking.
  * Dataset & Analytics: Clinical/simulated abdominal ultrasound recordings with specialized abnormal-only evaluation slice and quantitative metric pipelines.
* **Out-of-Scope:**
  * Real-time automated AI diagnosis/detection directly from video frames (this project focuses on capture, dictation, LLM structuring, and clinical evaluation).
  * Integration with proprietary closed-source PACS vendor hardware (simulated via standard frame grabber & video input).

---

## 4. Multidisciplinary 5-Member Team Responsibility Matrix

| Team Member | Department | Primary Responsibilities & Key Deliverables |
| :--- | :--- | :--- |
| **Member 1** | **CSE Core** (Core 1) | **Capture, Integration & Lead Systems Integrator**<br>• Frame grabber module & button-press frame save trigger<br>• Synchronous audio/mic recording pipeline<br>• Unified session JSON schema definition<br>• Owns weekly codebase merge and continuous integration across all 5 sub-modules |
| **Member 2** | **CSE Core** (Core 2) | **Speech Models & Pipeline Lead**<br>• Anatomical vocabulary-biased ASR pipeline implementation<br>• Audio preprocessing and phonetic dictionary integration<br>• Real-time speech streaming pipeline to structured text formatter |
| **Member 3** | **CSE DS** (Data Science) | **Data Science, Harness & Evaluation Lead**<br>• LLM model comparison harness (testing multiple open-weight LLMs)<br>• Curation of dataset splits (training, testing, and dedicated **abnormal-only slice**)<br>• Quantitative evaluation pipeline (WER, ROUGE, BLEU, clinical semantic similarity metrics)<br>• Statistical error analysis & performance benchmarking |
| **Member 4** | **IT** | **Interface, Audit & On-Prem Deployment**<br>• Review-and-correct UI screen for radiologists<br>• Full edit-logging & audit trail system (tracking radiologist modifications)<br>• On-premises serving infrastructure & containerized deployment (Docker)<br>• Access control, authentication, and local data security |
| **Member 5** | **Health Science** | **Clinical Lead & Domain Expert**<br>• Abdominal ultrasound report template taxonomy definition<br>• Clinical error severity rubric (critical, major, minor error classification)<br>• Ethics paperwork, IRB compliance, & radiologist scheduling<br>• Ground-truth annotation & qualitative clinical report validation |

---

## 5. System Architecture & Workflow Overview

```mermaid
flowchart TD
    subgraph Capture ["CSE Core 1: Capture & Integration"]
        US[Ultrasound Machine / Signal] --> FG[Frame Grabber & Button Trigger]
        RAD_MIC[Radiologist Dictation] --> MIC[Audio Recorder]
        FG --> SCHEMA[Session Schema Aggregator]
        MIC --> SCHEMA
    end

    subgraph Speech ["CSE Core 2: ASR Model"]
        SCHEMA --> ASR[Anatomical Vocabulary-Biased ASR]
    end

    subgraph DataScience ["CSE DS: Harness & Metrics"]
        ASR --> HARNESS[LLM Comparison Harness]
        SPLIT[(Dataset Splits: Inc. Abnormal Slice)] --> HARNESS
        HARNESS --> METRICS[Metrics Engine: WER, ROUGE, Error Benchmark]
        HARNESS --> DRAFT[Draft Structured Report]
    end

    subgraph Deployment ["IT: Interface & Serving"]
        DRAFT --> UI[Review & Correct Screen]
        UI --> AUDIT[Edit Logging & Access Control]
        UI --> ONPREM[On-Prem Storage / Final Report]
    end

    subgraph Clinical ["Health Science: Domain Lead"]
        HS[Health Science: Taxonomy & Error Severity Rubric] -.-> HARNESS
        HS -.-> UI
    end
```

---

## 6. Multi-Phase Project Roadmap (BAXXX191 Schedule)

```mermaid
gantt
    title Multidisciplinary Project Timeline (2026 - 2027)
    dateFormat  YYYY-MM-DD
    section Phase I: Planning & Scope
    Review-I Submission & Pitch           :done, 2026-09-16, 2026-09-25
    section Phase II: Core Execution (30%)
    Capture Module, ASR & Dataset Split   :active, 2026-09-26, 2026-10-23
    Review-II (30% Execution Demo)        :milestone, 2026-10-23, 2026-10-23
    section Phase III: Mid Execution (50%)
    LLM Harness, Metrics & UI Review      :2026-10-24, 2027-01-22
    Review-II Part B (50% Execution Demo) :milestone, 2027-01-22, 2027-01-22
    section Phase IV: Final Integration (100%)
    On-Prem Deploy & Clinical Evaluation  :2027-01-23, 2027-04-12
    Review-III & Final Report             :milestone, 2027-04-12, 2027-04-16
```
