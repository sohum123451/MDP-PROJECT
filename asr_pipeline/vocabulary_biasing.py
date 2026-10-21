"""
Anatomical Vocabulary Biasing Engine for Abdominal Ultrasound.
Provides prompt-biasing synthesis, hotword lexicon generation,
n-gram scoring, and quantitative clinical accuracy evaluation (WER and c-WER).
"""

import json
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional


class VocabularyBiasingEngine:
    """
    Biases ASR models toward abdominal ultrasound clinical terminology.
    Supports prefix prompt conditioning, hotword extraction, and clinical evaluation metrics.
    """

    def __init__(self, lexicon_path: Optional[str] = None):
        self.lexicon: Dict = {}
        self.anatomical_terms: Set[str] = set()
        self.pathology_terms: Set[str] = set()
        self.all_biased_terms: Set[str] = set()

        if lexicon_path:
            self.load_lexicon(lexicon_path)
        else:
            default_path = Path(__file__).parent.parent / "data" / "abdominal_ultrasound_lexicon.json"
            if default_path.exists():
                self.load_lexicon(str(default_path))

    def load_lexicon(self, filepath: str) -> None:
        """Parses the abdominal ultrasound lexicon and extracts biased token sets."""
        with open(filepath, "r", encoding="utf-8") as f:
            self.lexicon = json.load(f)

        categories = self.lexicon.get("categories", {})
        for cat_key, cat_val in categories.items():
            for term in cat_val.get("anatomical_structures", []):
                self.anatomical_terms.add(term.lower())
                self.all_biased_terms.add(term.lower())

            for term in cat_val.get("echogenicity_descriptors", []):
                self.all_biased_terms.add(term.lower())

            for term in cat_val.get("pathologies_and_findings", []):
                self.pathology_terms.add(term.lower())
                self.all_biased_terms.add(term.lower())

        # Also add individual significant words
        for phrase in list(self.all_biased_terms):
            for word in phrase.split():
                if len(word) > 4:
                    self.all_biased_terms.add(word)

    def generate_whisper_prompt(self, max_tokens: int = 120) -> str:
        """
        Constructs an optimal initial_prompt for Whisper models.
        Conditioning Whisper on this prefix biases its beam search decoder toward
        abdominal ultrasound anatomical structures and jargon.
        """
        key_terms = [
            "Abdominal ultrasound examination",
            "liver parenchyma",
            "hepatic steatosis",
            "hyperechoic lesion",
            "gallbladder wall thickening",
            "cholelithiasis",
            "posterior acoustic shadowing",
            "sonographic Murphy's sign",
            "common bile duct",
            "corticomedullary differentiation",
            "hydronephrosis",
            "nephrolithiasis",
            "renal calculus",
            "splenomegaly",
            "pancreatic duct of Wirsung",
            "abdominal aortic aneurysm",
            "mural thrombus",
            "Morison's pouch",
            "free peritoneal fluid"
        ]
        prompt = "Dictation context: " + ", ".join(key_terms) + "."
        return prompt

    def get_hotwords_list(self) -> List[str]:
        """Returns sorted list of priority medical hotwords for ASR beam search rescoring."""
        return sorted(list(self.all_biased_terms))

    def contains_anatomical_term(self, text: str) -> List[str]:
        """Detects and returns all biased anatomical terms found in a given text."""
        text_lower = text.lower()
        found = []
        for term in sorted(self.all_biased_terms, key=len, reverse=True):
            if term in text_lower:
                found.append(term)
        return found

    @staticmethod
    def calculate_wer(reference: str, hypothesis: str) -> float:
        """
        Computes standard Word Error Rate (WER = (Substitutions + Deletions + Insertions) / N).
        """
        ref_words = reference.lower().split()
        hyp_words = hypothesis.lower().split()

        n = len(ref_words)
        if n == 0:
            return 0.0 if len(hyp_words) == 0 else 1.0

        m = len(hyp_words)
        dp = [[0] * (m + 1) for _ in range(n + 1)]

        for i in range(n + 1):
            dp[i][0] = i
        for j in range(m + 1):
            dp[0][j] = j

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if ref_words[i - 1] == hyp_words[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i - 1][j],      # Deletion
                        dp[i][j - 1],      # Insertion
                        dp[i - 1][j - 1]   # Substitution
                    )

        return float(dp[n][m]) / float(n)

    def calculate_clinical_term_wer(
        self,
        reference: str,
        hypothesis: str
    ) -> Tuple[float, int, int]:
        """
        Calculates Clinical Term Word Error Rate (c-WER), which exclusively measures
        accuracy on domain-specific anatomical and pathology vocabulary.
        Returns: (c_wer, total_clinical_terms, missed_or_incorrect_terms)
        """
        ref_terms = self.contains_anatomical_term(reference)
        if not ref_terms:
            return 0.0, 0, 0

        hyp_lower = hypothesis.lower()
        missed = 0
        for term in ref_terms:
            if term not in hyp_lower:
                missed += 1

        c_wer = float(missed) / float(len(ref_terms))
        return round(c_wer, 4), len(ref_terms), missed
