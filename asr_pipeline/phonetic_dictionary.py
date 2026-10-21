"""
Phonetic Dictionary and Homophone Disambiguation Engine.
Resolves acoustically similar medical terms, segmented phonemes, and
transcription hallucinations into standardized abdominal ultrasound terminology.
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class PhoneticDictionary:
    """
    Medical phonetic dictionary tailored for abdominal ultrasound terminology.
    Implements rule-based substitution, double-metaphone inspired phonetic hashing,
    and Levenshtein-based fuzzy rescue for acoustically corrupted words.
    """

    def __init__(self, dictionary_path: Optional[str] = None):
        self.exact_substitutions: Dict[str, str] = {}
        self.phonetic_entries: List[Dict] = []
        self._compiled_regexes: List[Tuple[re.Pattern, str]] = []

        if dictionary_path:
            self.load_dictionary(dictionary_path)
        else:
            default_path = Path(__file__).parent.parent / "data" / "phonetic_corrections.json"
            if default_path.exists():
                self.load_dictionary(str(default_path))

    def load_dictionary(self, filepath: str) -> None:
        """Loads substitution mapping and phonetic medical dictionary from JSON."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.exact_substitutions = data.get("exact_phrase_substitutions", {})
        self.phonetic_entries = data.get("phonetic_medical_dictionary", [])

        # Compile phrase regexes sorted by descending phrase length (greedy matching)
        sorted_phrases = sorted(self.exact_substitutions.keys(), key=lambda k: len(k), reverse=True)
        self._compiled_regexes = [
            (re.compile(r"\b" + re.escape(phrase) + r"\b", re.IGNORECASE), replacement)
            for phrase, replacement in [(p, self.exact_substitutions[p]) for p in sorted_phrases]
        ]

    def soundex_encode(self, word: str) -> str:
        """
        Calculates Soundex code for an anatomical word.
        Retains first letter and encodes consonants into numerical sound classes.
        """
        word = word.upper().strip()
        if not word:
            return ""

        mapping = {
            "B": "1", "F": "1", "P": "1", "V": "1",
            "C": "2", "G": "2", "J": "2", "K": "2", "Q": "2", "S": "2", "X": "2", "Z": "2",
            "D": "3", "T": "3",
            "L": "4",
            "M": "5", "N": "5",
            "R": "6"
        }

        first_char = word[0]
        encoded = [first_char]

        prev_code = mapping.get(first_char, "")

        for char in word[1:]:
            code = mapping.get(char, "")
            if code and code != prev_code:
                encoded.append(code)
                prev_code = code
            elif char in "AEIOUYWH":
                prev_code = ""

        # Pad or trim to 4 characters
        result = "".join(encoded)
        result = (result + "000")[:4]
        return result

    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Computes edit distance between two strings."""
        if len(s1) < len(s2):
            return PhoneticDictionary.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def correct_phonetic_homophones(self, text: str) -> Tuple[str, List[Dict]]:
        """
        Applies known phonetic substitutions and multi-word phrase corrections.
        Returns the corrected text alongside a list of applied corrections.
        """
        corrected = text
        applied_corrections = []

        for pattern, replacement in self._compiled_regexes:
            match = pattern.search(corrected)
            if match:
                original = match.group(0)
                corrected = pattern.sub(replacement, corrected)
                applied_corrections.append({
                    "original": original,
                    "replacement": replacement,
                    "strategy": "exact_phonetic_phrase"
                })

        return corrected, applied_corrections

    def disambiguate_medical_term(
        self,
        token: str,
        max_edit_distance: int = 2,
        similarity_threshold: float = 0.75
    ) -> Optional[Tuple[str, float]]:
        """
        Searches the phonetic medical dictionary for terms matching an ambiguous word.
        Uses Soundex and Levenshtein similarity to find the most probable clinical match.
        """
        token_lower = token.lower().strip()
        if len(token_lower) <= 3:
            return None

        best_term = None
        best_score = 0.0

        token_soundex = self.soundex_encode(token_lower)

        for entry in self.phonetic_entries:
            target_term = entry["term"].lower()
            dist = self.levenshtein_distance(token_lower, target_term)

            max_len = max(len(token_lower), len(target_term))
            similarity = 1.0 - (dist / max_len)

            # Bonus if soundex matches
            target_soundex = self.soundex_encode(target_term)
            if token_soundex == target_soundex:
                similarity += 0.15

            if dist <= max_edit_distance and similarity >= similarity_threshold:
                if similarity > best_score:
                    best_score = similarity
                    best_term = entry["term"]

        if best_term:
            return best_term, min(1.0, best_score)
        return None

    def post_process_transcription(self, transcript: str) -> Tuple[str, List[Dict]]:
        """
        Full post-processing pipeline:
        1. Multi-word phrase substitutions
        2. Token-level fuzzy phonetic matching against clinical lexicon
        """
        # Phase 1: Multi-word phrase substitution
        text, corrections = self.correct_phonetic_homophones(transcript)

        # Phase 2: Token-level disambiguation
        words = text.split()
        modified_words = []

        for word in words:
            # Strip trailing punctuation for matching
            match = re.match(r"^([^\w]*)([\w-]+)([^\w]*)$", word)
            if match:
                prefix, core, suffix = match.groups()
                result = self.disambiguate_medical_term(core)
                if result and result[0].lower() != core.lower():
                    corrected_word = result[0]
                    corrections.append({
                        "original": core,
                        "replacement": corrected_word,
                        "strategy": "phonetic_fuzzy_match",
                        "confidence": round(result[1], 3)
                    })
                    modified_words.append(f"{prefix}{corrected_word}{suffix}")
                else:
                    modified_words.append(word)
            else:
                modified_words.append(word)

        return " ".join(modified_words), corrections
