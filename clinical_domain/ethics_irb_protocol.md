# Clinical Research & IRB Ethics Protocol Package
**Study Title:** Multimodal AI Integration for Abdominal Ultrasound Clinical Documentation: An Observational Validation Study  
**Lead Investigator:** Nikilan (Member 5 — Health Science Domain Lead)  
**Academic Course:** BAXXX191 Basic Multidisciplinary Project  
**Affiliated Hospital:** Department of Radiodiagnosis & Imaging  

---

## 1. Study Rationale & Ethical Foundation

The deployment of automated Speech-to-Text (ASR) and Large Language Model (LLM) structuring tools in clinical radiology carries substantial patient safety responsibilities. This protocol governs data governance, de-identification, radiologist consent, and prospective validation safeguards for the EchoScribe-AI platform.

---

## 2. Institutional Review Board (IRB) Protocol Summary

- **Study Type:** Non-interventional, observational validation study using de-identified ultrasound sessions.
- **Patient Risk Classification:** Minimal Risk (45 CFR § 46.102).
- **Informed Consent Waiver:** Approved under HHS regulations as retrospective/simulated audio dictations are scrubbed of all 18 HIPAA Safe Harbor Direct Identifiers prior to ingestion.
- **Physical Data Residence:** Strictly on-premises on local hospital servers. Cloud exfiltration of unencrypted voice or raw DICOM frames is prohibited.

---

## 3. Anonymization Protocol (HIPAA Safe Harbor Compliance)

1. **Audio Sanitization:** Names of patients, MRNs, dates of birth, and examining facilities are redacted prior to model ingestion.
2. **Video Frame Scrubbing:** Ultrasound frame grabber crops all burned-in patient header text fields (top 60 pixels of B-mode display) ensuring only anatomical ultrasound sector pixels are retained.
3. **Session Pseudonymization:** Replaced by cryptographic hashes (`ANON_PT_XXXXX`).
