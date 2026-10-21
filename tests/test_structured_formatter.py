"""
Unit Tests for Structured Text Formatter and Measurement Normalizer.
"""

from asr_pipeline.structured_formatter import StructuredTextFormatter
from asr_pipeline.session_models import AudioMetadata


def test_spoken_measurement_normalization():
    formatter = StructuredTextFormatter()

    text1 = "Gallbladder wall thickening measuring four point five millimeters."
    norm1, meas1 = formatter.normalize_spoken_measurements(text1)

    assert "4.5 mm" in norm1
    assert len(meas1) == 1
    assert meas1[0].value == 4.5
    assert meas1[0].unit == "mm"

    text2 = "Aortic aneurysm measuring four point eight centimeters."
    norm2, meas2 = formatter.normalize_spoken_measurements(text2)
    assert "4.8 cm" in norm2
    assert len(meas2) == 1
    assert meas2[0].value == 4.8
    assert meas2[0].unit == "cm"


def test_organ_classification():
    formatter = StructuredTextFormatter()

    assert formatter.classify_organ_context("Liver parenchyma demonstrates increased echogenicity.") == "liver"
    assert formatter.classify_organ_context("Gallbladder lumen contains multiple calculi.") == "gallbladder"
    assert formatter.classify_organ_context("Right kidney shows moderate hydronephrosis.") == "right_kidney"
    assert formatter.classify_organ_context("Pancreatic duct caliber is normal.") == "pancreas"
    assert formatter.classify_organ_context("Spleen craniocaudal length is 14 cm.") == "spleen"
    assert formatter.classify_organ_context("Abdominal aorta shows fusiform aneurysm.") == "aorta"
    assert formatter.classify_organ_context("Free anechoic fluid in Morison's pouch.") == "peritoneum"


def test_full_dictation_report_structuring():
    formatter = StructuredTextFormatter()

    raw = "The liver shows moderate stea tosis. Gall bladder has wall thickening measuring four point five millimeters with chole lithiasis."
    biased = "The liver shows moderate steatosis. Gallbladder has wall thickening measuring 4.5 mm with cholelithiasis."

    report = formatter.format_dictation(
        raw_text=raw,
        biased_text=biased,
        audio_metadata=AudioMetadata(sample_rate=16000, duration_seconds=5.0)
    )

    assert len(report.organ_findings) >= 2
    organs = [f.organ for f in report.organ_findings]
    assert "liver" in organs
    assert "gallbladder" in organs

    gb_finding = next(f for f in report.organ_findings if f.organ == "gallbladder")
    assert gb_finding.abnormality_detected is True
    assert any(m.value == 4.5 and m.unit == "mm" for m in gb_finding.measurements)
