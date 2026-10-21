"""
Benchmark Harness for Anatomical Vocabulary-Biased Speech Recognition.
Quantitatively compares Baseline Unbiased ASR against Anatomically-Biased ASR
across curated abdominal ultrasound clinical dictation cases.
"""

import json
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from asr_pipeline.vocabulary_biasing import VocabularyBiasingEngine
from asr_pipeline.phonetic_dictionary import PhoneticDictionary
from asr_pipeline.structured_formatter import StructuredTextFormatter


def run_benchmark():
    data_path = Path(__file__).parent.parent / "data" / "sample_transcripts.json"
    with open(data_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    biasing_engine = VocabularyBiasingEngine()
    phonetic_dict = PhoneticDictionary()
    formatter = StructuredTextFormatter(biasing_engine)

    cases = dataset.get("cases", [])
    print("=" * 80)
    print("  ECHOSCRIBE-AI / SONOASSIST: CSE CORE 2 ASR BENCHMARK EVALUATION")
    print("  Evaluating Anatomical Vocabulary-Biased ASR vs Unbiased Baseline")
    print("=" * 80)

    total_baseline_wer = 0.0
    total_biased_wer = 0.0
    total_baseline_cwer = 0.0
    total_biased_cwer = 0.0
    case_results = []

    for case in cases:
        case_id = case["id"]
        condition = case["clinical_condition"]
        gt = case["ground_truth"]
        unbiased_hyp = case["raw_unbiased_transcription"]

        # Run phonetic dictionary and vocabulary biasing post-processing
        biased_hyp, corrections = phonetic_dict.post_process_transcription(unbiased_hyp)

        # Normalize measurements in both
        unbiased_norm, _ = formatter.normalize_spoken_measurements(unbiased_hyp)
        biased_norm, _ = formatter.normalize_spoken_measurements(biased_hyp)

        # Compute Metrics
        base_wer = VocabularyBiasingEngine.calculate_wer(gt, unbiased_norm)
        bias_wer = VocabularyBiasingEngine.calculate_wer(gt, biased_norm)

        base_cwer, total_terms, base_missed = biasing_engine.calculate_clinical_term_wer(gt, unbiased_norm)
        bias_cwer, _, bias_missed = biasing_engine.calculate_clinical_term_wer(gt, biased_norm)

        total_baseline_wer += base_wer
        total_biased_wer += bias_wer
        total_baseline_cwer += base_cwer
        total_biased_cwer += bias_cwer

        case_results.append({
            "id": case_id,
            "condition": condition,
            "base_wer": round(base_wer * 100, 2),
            "bias_wer": round(bias_wer * 100, 2),
            "base_cwer": round(base_cwer * 100, 2),
            "bias_cwer": round(bias_cwer * 100, 2),
            "terms_total": total_terms,
            "base_missed": base_missed,
            "bias_missed": bias_missed,
            "corrections_applied": len(corrections)
        })

    num_cases = max(1, len(cases))
    avg_base_wer = (total_baseline_wer / num_cases) * 100.0
    avg_bias_wer = (total_biased_wer / num_cases) * 100.0
    avg_base_cwer = (total_baseline_cwer / num_cases) * 100.0
    avg_bias_cwer = (total_biased_cwer / num_cases) * 100.0

    wer_reduction = ((avg_base_wer - avg_bias_wer) / avg_base_wer) * 100.0 if avg_base_wer > 0 else 0.0
    cwer_reduction = ((avg_base_cwer - avg_bias_cwer) / avg_base_cwer) * 100.0 if avg_base_cwer > 0 else 0.0

    # Print Table
    print(f"\n{'Case ID':<14} | {'Condition':<34} | {'Base WER':<9} | {'Biased WER':<10} | {'Base c-WER':<10} | {'Biased c-WER':<12}")
    print("-" * 105)
    for res in case_results:
        print(f"{res['id']:<14} | {res['condition'][:34]:<34} | {res['base_wer']:>7.1f}% | {res['bias_wer']:>8.1f}% | {res['base_cwer']:>8.1f}% | {res['bias_cwer']:>10.1f}%")

    print("-" * 105)
    print(f"{'AVERAGE':<14} | {'Across All Test Cases':<34} | {avg_base_wer:>7.1f}% | {avg_bias_wer:>8.1f}% | {avg_base_cwer:>8.1f}% | {avg_bias_cwer:>10.1f}%")
    print("=" * 105)
    print(f"\n[SUMMARY BENCHMARK OUTCOMES]")
    print(f"  - Overall Word Error Rate (WER) Reduction:          {wer_reduction:.1f}% Relative Improvement")
    print(f"  - Clinical Term Word Error Rate (c-WER) Reduction:  {cwer_reduction:.1f}% Relative Improvement")
    print(f"  - Baseline Average Clinical Term WER:               {avg_base_cwer:.1f}%")
    print(f"  - Biased ASR Average Clinical Term WER:             {avg_bias_cwer:.1f}%\n")

    return {
        "avg_base_wer": avg_base_wer,
        "avg_bias_wer": avg_bias_wer,
        "avg_base_cwer": avg_base_cwer,
        "avg_bias_cwer": avg_bias_cwer,
        "wer_reduction_percent": wer_reduction,
        "cwer_reduction_percent": cwer_reduction,
        "case_results": case_results
    }


if __name__ == "__main__":
    run_benchmark()
