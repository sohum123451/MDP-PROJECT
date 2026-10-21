"""
Unit Tests for Phonetic Dictionary and Medical Homophone Disambiguation.
"""

from asr_pipeline.phonetic_dictionary import PhoneticDictionary


def test_soundex_encoding():
    pd = PhoneticDictionary()
    assert pd.soundex_encode("Robert") == "R163"
    assert pd.soundex_encode("Rupert") == "R163"
    assert len(pd.soundex_encode("hyperechoic")) == 4


def test_levenshtein_distance():
    assert PhoneticDictionary.levenshtein_distance("kitten", "sitting") == 3
    assert PhoneticDictionary.levenshtein_distance("calculus", "calculus") == 0
    assert PhoneticDictionary.levenshtein_distance("cholelithiasis", "cholelithiasis") == 0


def test_exact_phrase_substitutions():
    pd = PhoneticDictionary()

    raw_text = "The scan showed hyper a coick lesions and coal a cyst tight us with murphys sign."
    corrected, applied = pd.correct_phonetic_homophones(raw_text)

    assert "hyperechoic" in corrected
    assert "cholecystitis" in corrected
    assert "Murphy's sign" in corrected
    assert len(applied) >= 3


def test_medical_term_disambiguation():
    pd = PhoneticDictionary()

    # Slightly misspelled or acoustically ambiguous medical terms
    match = pd.disambiguate_medical_term("hiperechoic")
    assert match is not None
    assert match[0] == "hyperechoic"

    match_hydro = pd.disambiguate_medical_term("hydronefrosis")
    assert match_hydro is not None
    assert match_hydro[0] == "hydronephrosis"


def test_full_transcription_post_processing():
    pd = PhoneticDictionary()
    raw = "Patient has severe hydro nephrosis and spleno megaly noted in morrisons pouch."
    cleaned, corrections = pd.post_process_transcription(raw)

    assert "hydronephrosis" in cleaned
    assert "splenomegaly" in cleaned
    assert "Morison's pouch" in cleaned
    assert len(corrections) >= 3
