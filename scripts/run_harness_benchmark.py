"""
Data Science & Business Systems Benchmark Runner.
Member 3 (Manya - Business Systems & CSE DS Lead).
Demonstrates LLM Comparison Harness on the Abnormal-Only Evaluation Slice
and prints the Hospital Economic ROI Model.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from harness_and_analytics.dataset_splits import DatasetSplitManager
from harness_and_analytics.llm_comparison_harness import LLMComparisonHarness
from harness_and_analytics.business_roi_model import HospitalBusinessROIModel


def run_benchmark_and_roi():
    print("=" * 85)
    print("  ECHOSCRIBE-AI / SONOASSIST: DATA SCIENCE HARNESS & BUSINESS ROI SUITE")
    print("  Member 3 Deliverable: Business Systems & CSE DS (Manya)")
    print("=" * 85)

    # 1. Dataset Split & Abnormal-Only Slice
    split_mgr = DatasetSplitManager()
    abnormal_slice = split_mgr.get_abnormal_only_slice()
    print(f"\n[1] Dataset Slicing Complete:")
    print(f"    Total Curated Cases:             {len(split_mgr.cases)}")
    print(f"    Dedicated Abnormal-Only Slice:   {len(abnormal_slice)} acute pathology cases")
    print(f"    Conditions in Abnormal Slice:    {[c['clinical_condition'][:30] for c in abnormal_slice]}")

    # 2. LLM Model Comparison Harness
    harness = LLMComparisonHarness()
    print("\n[2] Executing LLM Comparison Harness across Open-Weight Models...")
    results = harness.evaluate_on_slice(abnormal_slice)

    print(f"\n{'Model Architecture':<22} | {'ROUGE-1':<9} | {'ROUGE-2':<9} | {'ROUGE-L':<9} | {'Entity F1':<11} | {'Latency':<10}")
    print("-" * 85)
    for model_id, m in results.items():
        print(f"{model_id:<22} | {m['avg_rouge_1']:>7.1f}% | {m['avg_rouge_2']:>7.1f}% | {m['avg_rouge_l']:>7.1f}% | {m['avg_entity_f1']:>9.1f}% | {m['avg_latency_ms']:>8.1f}ms")
    print("-" * 85)

    # 3. Hospital Business ROI Model
    roi_model = HospitalBusinessROIModel()
    metrics = roi_model.calculate_annual_metrics()

    print("\n[3] Hospital Economics & Operational Workflow Impact:")
    print(f"    Total Annual Ultrasound Exams:           {metrics['total_annual_ultrasound_exams']:,} scans")
    print(f"    Radiologist Minutes Saved per Exam:      {metrics['minutes_saved_per_exam']} mins (70.8% reduction)")
    print(f"    Physician Clinical Hours Recaptured:     {metrics['radiologist_hours_saved_annually']:,.1f} hours/year")
    print(f"    Transcription Outsourcing Elimination:   ${metrics['transcription_outsourcing_savings_usd']:,.2f}/year")
    print(f"    Total Net Annual Operational Benefit:    ${metrics['net_annual_benefit_usd']:,.2f}")
    print(f"    Capital Investment Payback Period:       {metrics['payback_period_months']} months")
    print(f"    3-Year Net Present Value (NPV):          ${metrics['three_year_npv_usd']:,.2f}")
    print(f"    3-Year Return on Investment (ROI):       {metrics['three_year_roi_percentage']:.1f}%")

    print("\n" + "=" * 85)
    print("  DATA SCIENCE & BUSINESS SYSTEMS VALIDATION COMPLETE (MEMBER 3)")
    print("=" * 85)


if __name__ == "__main__":
    run_benchmark_and_roi()
