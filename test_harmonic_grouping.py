#!/usr/bin/env python3
"""
Test script for harmonic series grouping function.

Demonstrates how group_peaks_into_harmonic_series() can separate
polyphonic material into individual notes/voices.
"""

import numpy as np
import soundfile as sf
import sys
sys.path.insert(0, '/Applications/AudioGuide/audioguide-claude')

from audioguide.spectralanalysis import extract_all_spectral_peaks, group_peaks_into_harmonic_series


def generate_harmonic_tone(frequency, duration, sr, n_harmonics=8, decay_rate=0.7):
    """Generate a synthetic tone with harmonics"""
    t = np.linspace(0, duration, int(sr * duration))
    signal = np.zeros_like(t)

    for n in range(1, n_harmonics + 1):
        amplitude = decay_rate ** (n - 1)  # Harmonics decay
        signal += amplitude * np.sin(2 * np.pi * frequency * n * t)

    # Normalize
    signal = signal / np.max(np.abs(signal))
    return signal


def generate_chord(frequencies, duration, sr):
    """Generate a chord by mixing multiple tones"""
    signals = [generate_harmonic_tone(f, duration, sr) for f in frequencies]
    chord = sum(signals)
    # Normalize
    chord = chord / np.max(np.abs(chord))
    return chord


def main():
    print("=" * 70)
    print("Testing Harmonic Series Grouping")
    print("=" * 70)

    # Parameters
    sr = 48000
    duration = 1.0

    # Test 1: C Major Chord (C4, E4, G4)
    print("\n### Test 1: C Major Chord (C4 + E4 + G4) ###\n")

    C4 = 261.63
    E4 = 329.63
    G4 = 392.00

    chord = generate_chord([C4, E4, G4], duration, sr)

    # Save audio for inspection
    output_path = '/Applications/AudioGuide/test_output/test_chord_c_major.wav'
    sf.write(output_path, chord, sr, subtype='PCM_24')
    print(f"Generated C major chord audio: {output_path}")

    # Extract all spectral peaks
    print("\n--- Extracting Spectral Peaks ---")
    peaks = extract_all_spectral_peaks(
        chord, sr,
        fmin=80, fmax=3000,
        min_amplitude_ratio=0.01,
        max_peaks=32
    )

    print(f"Found {len(peaks)} spectral peaks:")
    for i, (freq, amp) in enumerate(peaks[:10]):  # Show top 10
        print(f"  {i+1}. {freq:.2f} Hz  (amp: {amp:.2f})")
    if len(peaks) > 10:
        print(f"  ... and {len(peaks)-10} more")

    # Group into harmonic series
    print("\n--- Grouping into Harmonic Series ---")
    voices = group_peaks_into_harmonic_series(
        peaks,
        tolerance_cents=50,
        min_harmonics=3,
        max_voices=8
    )

    print(f"\nIdentified {len(voices)} voices:\n")

    for i, voice in enumerate(voices):
        print(f"Voice {i+1}: {voice['note_name']} ({voice['f0']:.2f} Hz)")
        print(f"  Strength: {voice['strength']:.2f}")
        print(f"  Harmonics found: {len(voice['harmonics'])}")
        print(f"  Harmonic numbers: {voice['harmonic_numbers']}")
        print(f"  Frequencies:")
        for freq, amp in voice['harmonics'][:5]:  # Show first 5
            print(f"    {freq:.2f} Hz (amp: {amp:.2f})")
        if len(voice['harmonics']) > 5:
            print(f"    ... and {len(voice['harmonics'])-5} more")
        print()

    # Verify we found the expected notes
    expected_notes = ['C4', 'E4', 'G4']
    found_notes = [v['note_name'] for v in voices]

    print("--- Verification ---")
    print(f"Expected notes: {expected_notes}")
    print(f"Found notes: {found_notes}")

    matches = sum(1 for note in expected_notes if note in found_notes)
    print(f"Match: {matches}/{len(expected_notes)} notes correctly identified")


    # Test 2: Single note (should identify as one voice)
    print("\n" + "=" * 70)
    print("### Test 2: Single Note (A4) ###\n")

    A4 = 440.0
    single_note = generate_harmonic_tone(A4, duration, sr)

    output_path = '/Applications/AudioGuide/test_output/test_single_note_A4.wav'
    sf.write(output_path, single_note, sr, subtype='PCM_24')
    print(f"Generated A4 note audio: {output_path}")

    peaks = extract_all_spectral_peaks(
        single_note, sr,
        fmin=80, fmax=3000,
        min_amplitude_ratio=0.01,
        max_peaks=32
    )

    voices = group_peaks_into_harmonic_series(
        peaks,
        tolerance_cents=50,
        min_harmonics=3,
        max_voices=8
    )

    print(f"\nIdentified {len(voices)} voice(s):")
    for voice in voices:
        print(f"  {voice['note_name']} ({voice['f0']:.2f} Hz) - {len(voice['harmonics'])} harmonics")

    print("\n" + "=" * 70)
    print("Harmonic grouping test complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
