"""
Structured Text Formatter for Abdominal Ultrasound Dictations.
Extracts anatomical entities, normalizes spoken numbers into metric measurements,
segments speech into organ sections, and evaluates clinical abnormalities.
"""

import re
from typing import List, Dict, Optional, Tuple
from asr_pipeline.session_models import (
    OrganFinding,
    ClinicalMeasurement,
    StructuredUltrasoundDictation,
    ASRSegment,
    AudioMetadata
)
from asr_pipeline.vocabulary_biasing import VocabularyBiasingEngine


class StructuredTextFormatter:
    """
    Parses biased ASR transcription streams into structured ultrasound report findings.
    """

    WORD_TO_NUMBER = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
        "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
        "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
        "eighty": 80, "ninety": 90, "point": "."
    }

    ORGAN_KEYWORDS = {
        "liver": ["liver", "hepatic", "portal vein", "riedel"],
        "gallbladder": ["gallbladder", "gall bladder", "chole", "biliary", "cystic duct", "cbd", "common bile duct"],
        "pancreas": ["pancreas", "pancreatic", "wirsung"],
        "spleen": ["spleen", "splenic"],
        "right_kidney": ["right kidney", "right renal"],
        "left_kidney": ["left kidney", "left renal"],
        "kidneys": ["kidney", "renal", "nephro", "pyelo", "calyceal", "caliceal", "corticomedullary"],
        "aorta": ["aorta", "aortic", "aneurysm", "ivc", "inferior vena cava"],
        "peritoneum": ["morison", "morrison", "ascites", "fluid", "peritoneal", "recess", "cul-de-sac"]
    }

    ABNORMAL_KEYWORDS = [
        "thickening", "calculus", "calculi", "cholelithiasis", "cholecystitis",
        "hydronephrosis", "steatosis", "cirrhosis", "hepatomegaly", "splenomegaly",
        "aneurysm", "thrombus", "mass", "lesion", "cyst", "hematoma",
        "dilatation", "shadowing", "murphy's sign is positive", "free fluid", "abnormal"
    ]

    def __init__(self, biasing_engine: Optional[VocabularyBiasingEngine] = None):
        self.biasing_engine = biasing_engine or VocabularyBiasingEngine()

    def normalize_spoken_measurements(self, text: str) -> Tuple[str, List[ClinicalMeasurement]]:
        """
        Converts verbal measurements like 'four point five millimeters' into '4.5 mm'.
        Returns normalized text and list of ClinicalMeasurement models.
        """
        measurements: List[ClinicalMeasurement] = []
        normalized_text = text

        # Regex for spoken decimals and units: e.g. "four point five millimeters" or "1.8 centimeters"
        pattern = re.compile(
            r"(\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
            r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|"
            r"thirty|forty|fifty|\d+(?:\.\d+)?)\s*(?:point\s*(?:zero|one|two|three|four|five|six|seven|eight|nine|\d+))?)\s*"
            r"(millimeters|millimeter|mm|centimeters|centimeter|cm)\b",
            re.IGNORECASE
        )

        for match in pattern.finditer(text):
            raw_mention = match.group(0)
            raw_num_str = match.group(1).lower().strip()
            unit_str = match.group(2).lower().strip()

            # Normalize unit
            std_unit = "mm" if "m" in unit_str and "c" not in unit_str else "cm"

            # Parse numeric value
            val = self._parse_spoken_number(raw_num_str)
            if val is not None:
                measurements.append(ClinicalMeasurement(
                    parameter="anatomical_dimension",
                    value=round(val, 2),
                    unit=std_unit,
                    raw_mention=raw_mention,
                    confidence=0.98
                ))
                # Substitute in text
                normalized_text = normalized_text.replace(raw_mention, f"{val:.1f} {std_unit}")

        return normalized_text, measurements

    def _parse_spoken_number(self, num_str: str) -> Optional[float]:
        """Converts strings like 'four point five' or '14.2' into float."""
        try:
            return float(num_str)
        except ValueError:
            pass

        tokens = num_str.split()
        if "point" in tokens:
            pt_idx = tokens.index("point")
            integer_parts = tokens[:pt_idx]
            decimal_parts = tokens[pt_idx + 1:]

            int_val = self._sum_word_numbers(integer_parts)
            dec_str = "".join(str(self.WORD_TO_NUMBER.get(w, 0)) for w in decimal_parts)
            try:
                return float(f"{int_val}.{dec_str}")
            except ValueError:
                return float(int_val)
        else:
            return float(self._sum_word_numbers(tokens))

    def _sum_word_numbers(self, words: List[str]) -> int:
        total = 0
        for w in words:
            if w in self.WORD_TO_NUMBER:
                total += self.WORD_TO_NUMBER[w]
            elif w.isdigit():
                total += int(w)
        return total

    def classify_organ_context(self, sentence: str) -> str:
        """Determines the primary organ referenced in a dictation sentence."""
        sentence_lower = sentence.lower()
        for organ, keywords in self.ORGAN_KEYWORDS.items():
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", sentence_lower):
                    return organ
        return "general"

    def format_dictation(
        self,
        raw_text: str,
        biased_text: str,
        audio_metadata: Optional[AudioMetadata] = None,
        segments: Optional[List[ASRSegment]] = None
    ) -> StructuredUltrasoundDictation:
        """
        Converts biased text and segments into a StructuredUltrasoundDictation report.
        """
        # Step 1: Normalize verbal measurements
        normalized_full, all_measurements = self.normalize_spoken_measurements(biased_text)

        # Step 2: Split into sentences and segment by organ
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", normalized_full) if s.strip()]

        organ_findings_map: Dict[str, Dict] = {}

        for sentence in sentences:
            organ = self.classify_organ_context(sentence)
            if organ not in organ_findings_map:
                organ_findings_map[organ] = {
                    "sentences": [],
                    "measurements": [],
                    "entities": [],
                    "echogenicity": [],
                    "abnormal": False
                }

            organ_findings_map[organ]["sentences"].append(sentence)

            # Check abnormalities
            s_lower = sentence.lower()
            if any(ab in s_lower for ab in self.ABNORMAL_KEYWORDS):
                organ_findings_map[organ]["abnormal"] = True

            # Extract anatomical entities
            entities = self.biasing_engine.contains_anatomical_term(sentence)
            organ_findings_map[organ]["entities"].extend(entities)

            # Extract echogenicity descriptors
            for echo in ["hyperechoic", "hypoechoic", "anechoic", "isoechoic", "homogeneous", "heterogeneous"]:
                if echo in s_lower:
                    organ_findings_map[organ]["echogenicity"].append(echo)

        # Build OrganFinding objects
        findings_list: List[OrganFinding] = []
        for organ, data in organ_findings_map.items():
            combined_text = " ".join(data["sentences"])
            # Match measurements within this sentence
            _, organ_meas = self.normalize_spoken_measurements(combined_text)

            abnormal = data["abnormal"]
            severity = "moderate" if abnormal and "severe" not in combined_text.lower() else (
                "severe" if "severe" in combined_text.lower() else ("normal" if not abnormal else "mild")
            )

            finding = OrganFinding(
                organ=organ if organ in OrganFinding.model_fields["organ"].annotation.__args__ else "general",
                raw_dictation=combined_text,
                normalized_text=combined_text,
                abnormality_detected=abnormal,
                severity=severity,
                measurements=organ_meas,
                anatomical_entities=list(set(data["entities"])),
                echogenicity_features=list(set(data["echogenicity"]))
            )
            findings_list.append(finding)

        return StructuredUltrasoundDictation(
            audio_metadata=audio_metadata or AudioMetadata(),
            full_raw_transcript=raw_text,
            full_biased_transcript=normalized_full,
            segments=segments or [],
            organ_findings=findings_list
        )
