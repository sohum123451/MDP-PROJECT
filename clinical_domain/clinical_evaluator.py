"""
Clinical Error Evaluator & Patient Safety Scoring Engine.
Member 5 (Nikilan - Health Science Lead Deliverable).
Systematically evaluates draft ultrasound reports against the Clinical Error Severity Rubric,
detecting critical diagnostic omissions, laterality errors, and metric unit distortions.
"""

import json
import re
from typing import Dict, Any, List, Tuple
from pathlib import Path


class ClinicalSafetyReport:
    """Detailed clinical safety evaluation outcome."""
    def __init__(
        self,
        safety_score: float,
        critical_errors: List[str],
        major_errors: List[str],
        minor_errors: List[str],
        is_clinically_safe: bool
    ):
        self.safety_score = safety_score
        self.critical_errors = critical_errors
        self.major_errors = major_errors
        self.minor_errors = minor_errors
        self.is_clinically_safe = is_clinically_safe

    def to_dict(self) -> Dict[str, Any]:
        return {
            "safety_score": round(self.safety_score, 1),
            "is_clinically_safe": self.is_clinically_safe,
            "error_counts": {
                "critical": len(self.critical_errors),
                "major": len(self.major_errors),
                "minor": len(self.minor_errors)
            },
            "critical_errors": self.critical_errors,
            "major_errors": self.major_errors,
            "minor_errors": self.minor_errors
        }


class ClinicalErrorEvaluator:
    """
    Evaluates clinical reports against the ACR-aligned error severity rubric.
    Enforces zero-tolerance safety validation for critical acute ultrasound conditions.
    """

    CRITICAL_PATHOLOGY_TERMS = [
        "acute cholecystitis",
        "cholelithiasis",
        "abdominal aortic aneurysm",
        "hydronephrosis",
        "hemoperitoneum"
    ]

    def __init__(self, rubric_path: str = None):
        if rubric_path:
            with open(rubric_path, "r", encoding="utf-8") as f:
                self.rubric = json.load(f)
        else:
            default_path = Path(__file__).parent / "clinical_error_rubric.json"
            with open(default_path, "r", encoding="utf-8") as f:
                self.rubric = json.load(f)

    def evaluate_report(
        self,
        ground_truth: str,
        generated_report: str
    ) -> ClinicalSafetyReport:
        """Compares generated report against clinical ground truth."""
        gt_lower = ground_truth.lower()
        gen_lower = generated_report.lower()

        critical_errors: List[str] = []
        major_errors: List[str] = []
        minor_errors: List[str] = []

        # 1. Critical pathology omission check
        for pathology in self.CRITICAL_PATHOLOGY_TERMS:
            if pathology in gt_lower and pathology not in gen_lower:
                # Check for synonym
                if pathology == "cholelithiasis" and ("calculi" in gen_lower or "gallstone" in gen_lower):
                    continue
                critical_errors.append(f"Critical omission: Missing vital diagnosis '{pathology}' present in ground truth.")

        # 2. Laterality check (Left vs Right Kidney)
        if "right kidney" in gt_lower and "calculus" in gt_lower:
            if "left kidney" in gen_lower and "calculus" in gen_lower and "right kidney" not in gen_lower:
                critical_errors.append("Critical error: Renal calculus laterality transposed from Right to Left kidney.")

        # 3. Major error check: Measurement unit distortion (e.g. mm vs cm distortion)
        gt_mm_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:mm|millimeters)", gt_lower)
        gen_cm_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:cm|centimeters)", gen_lower)
        for val in gt_mm_matches:
            if val in gen_cm_matches and float(val) > 3.0:
                major_errors.append(f"Major error: Measurement '{val}' reported in centimeters instead of millimeters (factor of 10 error).")

        # 4. Murphy's sign check
        if "murphy's sign is positive" in gt_lower and "murphy" not in gen_lower:
            major_errors.append("Major omission: Omitted positive sonographic Murphy's sign in symptomatic gallbladder examination.")

        # Calculate safety score (100 - penalties)
        score = 100.0 - (len(critical_errors) * 50.0) - (len(major_errors) * 20.0) - (len(minor_errors) * 5.0)
        score = max(0.0, score)

        is_safe = (len(critical_errors) == 0 and score >= 80.0)

        return ClinicalSafetyReport(
            safety_score=score,
            critical_errors=critical_errors,
            major_errors=major_errors,
            minor_errors=minor_errors,
            is_clinically_safe=is_safe
        )
