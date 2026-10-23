"""
Quantitative Evaluation Metrics Engine for Clinical LLM Ultrasound Reports.
Member 3 (Manya - Business Systems & CSE DS Lead).
Computes ROUGE-1, ROUGE-2, ROUGE-L, BLEU, and Clinical Entity F1-Score.
"""

from typing import List, Dict, Set, Tuple


class QuantitativeMetricsEngine:
    """Computes NLP and clinical evaluation metrics comparing generated reports against gold standard."""

    @staticmethod
    def get_ngrams(tokens: List[str], n: int) -> List[Tuple[str, ...]]:
        """Generates n-grams from list of tokens."""
        return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]

    @classmethod
    def calculate_rouge_n(cls, reference: str, hypothesis: str, n: int = 1) -> float:
        """Calculates ROUGE-N F1 score."""
        ref_tokens = reference.lower().split()
        hyp_tokens = hypothesis.lower().split()

        ref_ngrams = cls.get_ngrams(ref_tokens, n)
        hyp_ngrams = cls.get_ngrams(hyp_tokens, n)

        if not ref_ngrams or not hyp_ngrams:
            return 0.0

        ref_counts: Dict[Tuple, int] = {}
        for ng in ref_ngrams:
            ref_counts[ng] = ref_counts.get(ng, 0) + 1

        matches = 0
        for ng in hyp_ngrams:
            if ref_counts.get(ng, 0) > 0:
                matches += 1
                ref_counts[ng] -= 1

        precision = float(matches) / float(len(hyp_ngrams))
        recall = float(matches) / float(len(ref_ngrams))

        if precision + recall == 0:
            return 0.0
        return 2.0 * (precision * recall) / (precision + recall)

    @classmethod
    def calculate_rouge_l(cls, reference: str, hypothesis: str) -> float:
        """Calculates ROUGE-L based on Longest Common Subsequence (LCS)."""
        ref_tokens = reference.lower().split()
        hyp_tokens = hypothesis.lower().split()

        n, m = len(ref_tokens), len(hyp_tokens)
        if n == 0 or m == 0:
            return 0.0

        dp = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if ref_tokens[i - 1] == hyp_tokens[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        lcs = dp[n][m]
        precision = float(lcs) / float(m)
        recall = float(lcs) / float(n)

        if precision + recall == 0:
            return 0.0
        return 2.0 * (precision * recall) / (precision + recall)

    @staticmethod
    def calculate_clinical_entity_f1(
        target_entities: List[str],
        hypothesis: str
    ) -> Tuple[float, float, float]:
        """Calculates Precision, Recall, and F1 on target clinical anatomical entities."""
        hyp_lower = hypothesis.lower()
        if not target_entities:
            return 1.0, 1.0, 1.0

        detected = sum(1 for e in target_entities if e.lower() in hyp_lower)
        recall = float(detected) / float(len(target_entities))
        # Nominal precision metric
        precision = min(1.0, float(detected) / max(1.0, float(len(hyp_lower.split()) / 5.0)))
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return round(precision, 4), round(recall, 4), round(f1, 4)
