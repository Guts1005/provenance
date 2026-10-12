"""
Generates high-precision 44.1kHz 16-bit PCM WAV audio assets for warehouse scanner feedback.
Simulates Zebra / Honeywell industrial barcode scanners and modern POS verification tones.
100% standard library (wave, math, struct) - zero external dependencies.
"""

import os
import wave
import math
import struct

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)
SAMPLE_RATE = 44100


def write_wav(filename: str, samples: list[float], sample_rate: int = SAMPLE_RATE):
    filepath = os.path.join(AUDIO_DIR, filename)
    with wave.open(filepath, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit (2 bytes per sample)
        wav_file.setframerate(sample_rate)

        packed_frames = bytearray()
        for s in samples:
            # Clamp between -1.0 and 1.0
            clamped = max(-1.0, min(1.0, s))
            int_sample = int(clamped * 32767.0)
            packed_frames.extend(struct.pack("<h", int_sample))

        wav_file.writeframes(packed_frames)
    print(f"Generated {filepath} ({len(samples)} samples, {len(samples)/sample_rate*1000:.1f}ms)")


def generate_scan_beep():
    """Classic Honeywell/Zebra high-pitch 2600Hz good-read chirp."""
    duration_s = 0.065
    total_samples = int(SAMPLE_RATE * duration_s)
    freq = 2600.0
    samples = []

    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Envelope: 4ms smooth cosine attack, sustain, 15ms decay
        if t < 0.004:
            env = 0.5 * (1.0 - math.cos(math.pi * t / 0.004))
        elif t > duration_s - 0.015:
            decay_t = (duration_s - t) / 0.015
            env = decay_t ** 1.5
        else:
            env = 1.0

        # Primary frequency + subtle 2nd harmonic (adds crisp optical click)
        val = 0.85 * math.sin(2.0 * math.pi * freq * t) + 0.15 * math.sin(2.0 * math.pi * freq * 2.0 * t)
        samples.append(val * env * 0.75)

    write_wav("scanner-beep.wav", samples)


def generate_finish_chime():
    """Satisfying two-tone ascending confirmation chime (E5 -> B5)."""
    tone1_freq = 659.25  # E5
    tone2_freq = 987.77  # B5
    t1_dur = 0.075
    t2_dur = 0.130
    total_samples = int(SAMPLE_RATE * (t1_dur + t2_dur))
    samples = []

    t1_samples = int(SAMPLE_RATE * t1_dur)
    for i in range(t1_samples):
        t = i / SAMPLE_RATE
        env = min(1.0, t / 0.006) * (1.0 - (t / t1_dur) * 0.3)
        val = math.sin(2.0 * math.pi * tone1_freq * t)
        samples.append(val * env * 0.7)

    t2_samples = total_samples - t1_samples
    for i in range(t2_samples):
        t = i / SAMPLE_RATE
        # Exponential ringing decay
        env = min(1.0, t / 0.005) * math.exp(-t * 18.0)
        val = 0.8 * math.sin(2.0 * math.pi * tone2_freq * t) + 0.2 * math.sin(2.0 * math.pi * tone2_freq * 2.0 * t)
        samples.append(val * env * 0.8)

    write_wav("scanner-finish.wav", samples)


def generate_error_buzz():
    """Low-frequency double-buzz warning for duplicate/invalid scan."""
    buzz_freq = 220.0
    pulse_dur = 0.065
    gap_dur = 0.035
    samples = []

    def make_pulse():
        pulse_samples = int(SAMPLE_RATE * pulse_dur)
        for i in range(pulse_samples):
            t = i / SAMPLE_RATE
            env = min(1.0, t / 0.005) * max(0.0, 1.0 - (t / pulse_dur) ** 2)
            # Mixed square/saw waveform for buzz texture
            val = (
                0.6 * math.sin(2.0 * math.pi * buzz_freq * t)
                + 0.25 * math.sin(2.0 * math.pi * buzz_freq * 3.0 * t)
                + 0.15 * math.sin(2.0 * math.pi * buzz_freq * 5.0 * t)
            )
            samples.append(val * env * 0.7)

    make_pulse()
    # Gap
    gap_samples = int(SAMPLE_RATE * gap_dur)
    samples.extend([0.0] * gap_samples)
    make_pulse()

    write_wav("scanner-error.wav", samples)


def generate_delete_sound():
    """Sleek descending purge tone for permanent footage deletion."""
    duration_s = 0.110
    total_samples = int(SAMPLE_RATE * duration_s)
    samples = []

    for i in range(total_samples):
        t = i / SAMPLE_RATE
        frac = t / duration_s
        freq = 520.0 - (frac * 260.0)  # Descends from 520Hz to 260Hz
        env = min(1.0, t / 0.005) * (1.0 - frac)
        val = math.sin(2.0 * math.pi * freq * t)
        samples.append(val * env * 0.6)

    write_wav("scanner-delete.wav", samples)


if __name__ == "__main__":
    generate_scan_beep()
    generate_finish_chime()
    generate_error_buzz()
    generate_delete_sound()
    print("All scanner audio assets generated successfully in ui/audio/.")
