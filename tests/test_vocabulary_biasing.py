"""
Unit Tests for Vocabulary Biasing Engine and Word Error Rate (WER/c-WER) Metrics.
"""

from asr_pipeline.vocabulary_biasing import VocabularyBiasingEngine


def test_lexicon_loading_and_hotwords():
    engine = VocabularyBiasingEngine()
    hotwords = engine.get_hotwords_list()

    assert len(hotwords) > 30
    assert "hyperechoic" in engine.all_biased_terms
    assert "cholelithiasis" in engine.all_biased_terms
    assert "hydronephrosis" in engine.all_biased_terms
    assert "aorta" in engine.all_biased_terms


def test_whisper_prompt_generation():
    engine = VocabularyBiasingEngine()
    prompt = engine.generate_whisper_prompt()

    assert "Abdominal ultrasound examination" in prompt
    assert "liver parenchyma" in prompt
    assert "cholelithiasis" in prompt
    assert len(prompt) > 50


def test_wer_calculation():
    # Exact match -> 0 WER
    assert VocabularyBiasingEngine.calculate_wer("normal liver parenchyma", "normal liver parenchyma") == 0.0

    # 1 substitution out of 3 -> 0.333
    wer = VocabularyBiasingEngine.calculate_wer("normal liver parenchyma", "normal liver tissue")
    assert round(wer, 2) == 0.33

    # Empty reference
    assert VocabularyBiasingEngine.calculate_wer("", "some hypothesis") == 1.0


def test_clinical_term_wer():
    engine = VocabularyBiasingEngine()
    gt = "Gallbladder shows cholelithiasis and wall thickening."
    # Both clinical terms preserved
    hyp_good = "Gallbladder shows cholelithiasis and wall thickening."
    cwer_good, total_terms, missed = engine.calculate_clinical_term_wer(gt, hyp_good)
    assert cwer_good == 0.0
    assert missed == 0

    # Terms missing or corrupted
    hyp_bad = "Gallbladder shows stones and something else."
    cwer_bad, _, missed_bad = engine.calculate_clinical_term_wer(gt, hyp_bad)
    assert cwer_bad > 0.0
    assert missed_bad > 0
