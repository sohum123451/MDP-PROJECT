"""
Unit Tests for Clinical Domain & Safety Evaluator (Nikilan - Health Science Lead).
"""

from clinical_domain.clinical_evaluator import ClinicalErrorEvaluator


def test_clinical_evaluator_clean_pass():
    evaluator = ClinicalErrorEvaluator()
    gt = "Gallbladder demonstrates diffuse wall thickening measuring 4.5 mm with cholelithiasis and positive Murphy's sign."
    gen = "Gallbladder demonstrates diffuse wall thickening measuring 4.5 mm with cholelithiasis and positive Murphy's sign."

    report = evaluator.evaluate_report(gt, gen)
    assert report.is_clinically_safe is True
    assert report.safety_score == 100.0
    assert len(report.critical_errors) == 0


def test_clinical_evaluator_critical_error_penalty():
    evaluator = ClinicalErrorEvaluator()
    gt = "Patient has severe acute cholecystitis with multiple calculi."
    gen = "Patient has normal gallbladder with no findings."

    report = evaluator.evaluate_report(gt, gen)
    assert report.is_clinically_safe is False
    assert report.safety_score <= 50.0
    assert len(report.critical_errors) >= 1


def test_measurement_unit_distortion_detection():
    evaluator = ClinicalErrorEvaluator()
    gt = "Gallbladder wall thickening measuring 4.5 mm."
    gen = "Gallbladder wall thickening measuring 4.5 cm."

    report = evaluator.evaluate_report(gt, gen)
    assert len(report.major_errors) >= 1
    assert "centimeters instead of millimeters" in report.major_errors[0]
