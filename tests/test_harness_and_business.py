"""
Unit Tests for LLM Comparison Harness & Business ROI Engine (Manya - Business Systems & DS).
"""

from harness_and_analytics.dataset_splits import DatasetSplitManager
from harness_and_analytics.quantitative_metrics import QuantitativeMetricsEngine
from harness_and_analytics.llm_comparison_harness import LLMComparisonHarness
from harness_and_analytics.business_roi_model import HospitalBusinessROIModel


def test_abnormal_only_slice_isolation():
    mgr = DatasetSplitManager()
    abnormal_slice = mgr.get_abnormal_only_slice()
    assert len(abnormal_slice) >= 4
    for c in abnormal_slice:
        assert c["is_abnormal"] is True


def test_quantitative_metrics_calculation():
    engine = QuantitativeMetricsEngine()
    ref = "The gallbladder shows diffuse wall thickening measuring 4.5 mm with cholelithiasis."
    hyp = "The gallbladder shows diffuse wall thickening measuring 4.5 mm with cholelithiasis."

    r1 = engine.calculate_rouge_n(ref, hyp, n=1)
    rl = engine.calculate_rouge_l(ref, hyp)
    assert r1 == 1.0
    assert rl == 1.0

    entities = ["gallbladder", "cholelithiasis", "wall thickening"]
    p, r, f1 = engine.calculate_clinical_entity_f1(entities, hyp)
    assert r == 1.0
    assert f1 > 0.0


def test_llm_harness_execution():
    harness = LLMComparisonHarness()
    mgr = DatasetSplitManager()
    cases = mgr.get_abnormal_only_slice()[:2]

    results = harness.evaluate_on_slice(cases)
    assert "LLaMA-3-8B" in results
    assert "Mistral-7B" in results
    assert results["LLaMA-3-8B"]["avg_rouge_l"] > 75.0


def test_hospital_business_roi_model():
    model = HospitalBusinessROIModel(
        num_ultrasound_machines=2,
        exams_per_day_per_machine=15,
        working_days_per_year=250
    )
    metrics = model.calculate_annual_metrics()

    assert metrics["total_annual_ultrasound_exams"] == 7500
    assert metrics["minutes_saved_per_exam"] == 8.5
    assert metrics["radiologist_hours_saved_annually"] > 1000.0
    assert metrics["payback_period_months"] < 12.0
    assert metrics["three_year_roi_percentage"] > 100.0
