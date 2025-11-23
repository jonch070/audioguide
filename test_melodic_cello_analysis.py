#!/usr/bin/env python3
"""
Analyze Staub-MelodicCello.wav to detect polyphonic content using harmonic grouping.

This script examines several segments of the cello piece to identify:
- How many voices are present in each segment
- What notes/frequencies are being played
- Whether the material is truly polyphonic or monophonic
"""

import numpy as np
import soundfile as sf
import sys
sys.path.insert(0, '/Applications/AudioGuide/audioguide-claude')

from audioguide.spectralanalysis import extract_all_spectral_peaks, group_peaks_into_harmonic_series


def analyze_audio_segment(audio, sr, start_sec, duration_sec, segment_name):
    """Analyze a specific time segment of the audio"""
    start_sample = int(start_sec * sr)
    end_sample = int((start_sec + duration_sec) * sr)
    segment = audio[start_sample:end_sample]

    print(f"\n{'='*70}")
    print(f"Segment: {segment_name}")
    print(f"Time: {start_sec:.2f}s - {start_sec + duration_sec:.2f}s")
    print(f"{'='*70}")

    # Extract spectral peaks
    peaks = extract_all_spectral_peaks(
        segment, sr,
        fmin=60,      # Lower for cello (C2 = 65 Hz)
        fmax=3000,    # Upper harmonics
        min_amplitude_ratio=0.02,  # 2% threshold
        max_peaks=40   # Allow more peaks for potential polyphony
    )

    print(f"\nFound {len(peaks)} spectral peaks")
    print("\nTop 10 peaks:")
    for i, (freq, amp) in enumerate(peaks[:10]):
        print(f"  {i+1}. {freq:7.2f} Hz  (amp: {amp:8.2f})")

    # Group into harmonic series
    voices = group_peaks_into_harmonic_series(
        peaks,
        tolerance_cents=50,
        min_harmonics=3,
        max_voices=6
    )

    print(f"\n--- Harmonic Analysis ---")
    print(f"Identified {len(voices)} voice(s):\n")

    if len(voices) == 0:
        print("  No clear harmonic series detected")
        print("  (May be inharmonic, noisy, or very weak signal)")

    for i, voice in enumerate(voices):
        print(f"Voice {i+1}: {voice['note_name']} ({voice['f0']:.2f} Hz)")
        print(f"  Harmonics found: {len(voice['harmonics'])}")
        print(f"  Harmonic numbers: {voice['harmonic_numbers']}")
        print(f"  Strength: {voice['strength']:.2f}")
        print(f"  Frequencies: ", end="")
        freqs = [f"{freq:.1f}" for freq, _ in voice['harmonics'][:5]]
        print(", ".join(freqs) + ("..." if len(voice['harmonics']) > 5 else ""))
        print()

    # Analysis
    if len(voices) == 1:
        print("→ Analysis: MONOPHONIC (single note)")
    elif len(voices) == 2:
        print("→ Analysis: POTENTIALLY POLYPHONIC (double-stop or harmonic)")
    elif len(voices) >= 3:
        print("→ Analysis: POLYPHONIC (chord or multiple voices)")

    return voices


def main():
    print("="*70)
    print("Melodic Cello Polyphonic Analysis")
    print("="*70)

    # Load audio
    audio_path = '/Users/jonathankawchuk/Documents/Max 9/Packages/Data Knot/media/Musical Examples/Staub-MelodicCello.wav'
    audio, sr = sf.read(audio_path)

    print(f"\nFile: Staub-MelodicCello.wav")
    print(f"Duration: {len(audio)/sr:.2f}s")
    print(f"Sample rate: {sr} Hz")
    print(f"Channels: {'Mono' if audio.ndim == 1 else 'Stereo'}")

    # Analyze several segments throughout the piece
    segments = [
        (0.5, 1.0, "Opening"),
        (5.0, 1.0, "Early section"),
        (10.0, 1.0, "Mid section 1"),
        (15.0, 1.0, "Mid section 2"),
        (20.0, 1.0, "Later section"),
        (25.0, 1.0, "Near end"),
    ]

    all_voices = []
    for start, duration, name in segments:
        if start + duration <= len(audio)/sr:
            voices = analyze_audio_segment(audio, sr, start, duration, name)
            all_voices.append((name, len(voices), voices))

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    voice_counts = [count for _, count, _ in all_voices]
    avg_voices = np.mean(voice_counts)
    max_voices = max(voice_counts)

    print(f"\nSegments analyzed: {len(all_voices)}")
    print(f"Average voices per segment: {avg_voices:.1f}")
    print(f"Maximum voices detected: {max_voices}")

    print("\nVoice distribution:")
    for name, count, voices in all_voices:
        marker = "●" * count if count > 0 else "○"
        notes = ", ".join([v['note_name'] for v in voices]) if voices else "none"
        print(f"  {name:20s} {marker:10s} ({count} voice{'s' if count != 1 else ''}: {notes})")

    # Recommendation
    print("\n--- Recommendation ---")
    if avg_voices < 1.5:
        print("This appears to be PREDOMINANTLY MONOPHONIC material.")
        print("Regular spectral reconstruction should work well.")
        print("Suggested: SPECTRAL_MAX_PARTIALS = 4-8")
    elif avg_voices < 2.5:
        print("This appears to be MIXED: mostly monophonic with some double-stops.")
        print("Voice grouping could help separate simultaneous notes.")
        print("Suggested: SPECTRAL_MAX_PARTIALS = 12-16")
    else:
        print("This appears to be POLYPHONIC material (chords/multiple voices).")
        print("Voice grouping would be beneficial for separation.")
        print("Suggested: SPECTRAL_MAX_PARTIALS = 16-24, enable voice grouping")

    print("\n" + "="*70)


if __name__ == '__main__':
    main()
