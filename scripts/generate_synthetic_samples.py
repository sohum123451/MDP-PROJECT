"""
Synthetic Audio Sample Generator for Abdominal Ultrasound ASR Testing.
Generates compliant 16kHz 16-bit mono WAV audio waveforms with simulated speech energy bursts
for automated pipeline integration tests and demonstrations.
"""

import math
import wave
import struct
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def generate_synthetic_ultrasound_audio(
    output_wav_path: str,
    duration_seconds: float = 4.0,
    sample_rate: int = 16000
) -> str:
    """
    Synthesizes a 16kHz mono audio WAV file containing harmonic speech-like formant tones
    alternating with brief inter-syllable pauses to test VAD and streaming chunk buffers.
    """
    total_samples = int(duration_seconds * sample_rate)
    samples = []

    # Frequencies simulating vocal tract fundamentals and first formants (F0 ~ 130Hz, F1 ~ 500Hz)
    f0 = 135.0
    f1 = 520.0

    for i in range(total_samples):
        t = float(i) / float(sample_rate)
        # Create 1.5s active speech bursts followed by 0.3s pause
        cycle = t % 1.8
        if cycle < 1.4:
            # Active speech envelope with slight amplitude modulation
            envelope = math.sin(math.pi * (cycle / 1.4)) ** 0.5
            val = 0.6 * math.sin(2.0 * math.pi * f0 * t) + 0.4 * math.sin(2.0 * math.pi * f1 * t)
            # Add small random dither
            sample = int(envelope * val * 22000.0)
        else:
            # Silence / ambient noise floor
            sample = int(50.0 * math.sin(2.0 * math.pi * 60.0 * t))

        samples.append(sample)

    output_path = Path(output_wav_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for s in samples:
            wf.writeframes(struct.pack("<h", max(-32768, min(32767, s))))

    return str(output_path)


if __name__ == "__main__":
    out_file = PROJECT_ROOT / "data" / "synthetic_test_dictation.wav"
    path = generate_synthetic_ultrasound_audio(str(out_file), duration_seconds=5.0)
    print(f"Generated synthetic test audio at: {path}")
