# Harmonic Series Grouping for Polyphonic Analysis

**Status:** Implemented and tested (November 17, 2025)
**Location:** `audioguide/spectralanalysis.py` (lines 279-386)

---

## Overview

The **harmonic series grouping** function enables AudioGuide to separate polyphonic material (chords, multiple notes) into individual voices by identifying which spectral peaks form harmonic relationships.

This is a **research/analysis tool** that can inform future spectral reconstruction enhancements, such as:
- Per-note reconstruction from chord progressions
- Separate track groups per voice in Reaper output
- Voice-specific processing and amplitude control

---

## How It Works

### Algorithm

1. **Extract all spectral peaks** using `extract_all_spectral_peaks()`
2. **Test each peak as a potential fundamental**:
   - Search for harmonics at 2×, 3×, 4×, etc. of the fundamental frequency
   - Match peaks within tolerance (e.g., ±50 cents)
3. **Accept voices with enough harmonics** (default: minimum 3)
4. **Assign peaks to voices** (each peak belongs to only one voice)
5. **Sort by strength** (sum of harmonic amplitudes)

### Function Signature

```python
def group_peaks_into_harmonic_series(
    peaks,                  # List of (frequency, amplitude) tuples
    tolerance_cents=50,     # Frequency matching tolerance
    min_harmonics=3,        # Minimum harmonics to identify a voice
    max_voices=8            # Maximum voices to identify
):
    """Returns list of voice dictionaries"""
```

### Output Structure

Each voice dictionary contains:
```python
{
    'f0': 261.63,                      # Fundamental frequency (Hz)
    'note_name': 'C4',                 # Musical note name
    'harmonics': [(261, 3138), ...],   # List of (freq, amp) tuples
    'harmonic_numbers': [1, 2, 4, 5],  # Which harmonics were found
    'strength': 8733.55                # Combined amplitude of all harmonics
}
```

---

## Test Results

### C Major Chord (C4 + E4 + G4)

**Input:** Synthetic chord with 8 harmonics per note
**Spectral peaks detected:** 22 peaks
**Voices identified:** 3/3 correct

| Voice | Fundamental | Harmonics Found | Strength | Note Name |
|-------|-------------|-----------------|----------|-----------|
| 1     | 392.00 Hz   | 7               | 11927.91 | G4        |
| 2     | 330.00 Hz   | 8               | 10686.04 | E4        |
| 3     | 262.00 Hz   | 7               | 8733.55  | C4        |

**Analysis:**
- All 3 notes correctly identified with correct note names
- Voices sorted by strength (G4 loudest, then E4, then C4)
- Each voice found 7-8 harmonics from the original 8
- No false positives (no extra voices detected)

### Single Note (A4)

**Input:** Single A4 (440 Hz) with harmonics
**Voices identified:** 1 (correct)

| Voice | Fundamental | Harmonics Found | Note Name |
|-------|-------------|-----------------|-----------|
| 1     | 440.00 Hz   | 6               | A4        |

---

## Usage Example

```python
from audioguide.spectralanalysis import (
    extract_all_spectral_peaks,
    group_peaks_into_harmonic_series
)

# Step 1: Extract spectral peaks
peaks = extract_all_spectral_peaks(
    audio_signal, sample_rate,
    fmin=80, fmax=3000,
    min_amplitude_ratio=0.01,
    max_peaks=32
)

# Step 2: Group into harmonic series
voices = group_peaks_into_harmonic_series(
    peaks,
    tolerance_cents=50,
    min_harmonics=3,
    max_voices=8
)

# Step 3: Process each voice
for voice in voices:
    print(f"Note: {voice['note_name']} ({voice['f0']:.2f} Hz)")
    print(f"  Harmonics: {len(voice['harmonics'])}")
    print(f"  Strength: {voice['strength']:.2f}")

    # Optionally reconstruct each voice separately
    # spectral_reconstruct_voice(voice['harmonics'], corpus)
```

---

## Test Script

A standalone test script is available:

**Location:** `/Applications/AudioGuide/audioguide-claude/test_harmonic_grouping.py`

**Usage:**
```bash
python3 test_harmonic_grouping.py
```

**Generates:**
- `/Applications/AudioGuide/test_output/test_chord_c_major.wav` - C major chord
- `/Applications/AudioGuide/test_output/test_single_note_A4.wav` - A4 note
- Console output showing identified voices and verification

---

## Parameters

### `tolerance_cents` (default: 50)

Frequency matching tolerance in cents (100 cents = 1 semitone).

- **50 cents**: Good for chromatic corpus (matches within quarter-tone)
- **25 cents**: Stricter matching for precise tuning
- **100 cents**: Looser matching for detuned/inharmonic material

### `min_harmonics` (default: 3)

Minimum number of harmonics required to accept a voice.

- **3**: Good balance (fundamental + 2 harmonics minimum)
- **4-5**: Stricter (reduces false positives)
- **2**: More lenient (may accept weak/noisy tones)

### `max_voices` (default: 8)

Maximum number of voices to identify.

- **3-4**: Typical chord voicing
- **6-8**: Dense polyphony (e.g., jazz voicings)
- **1-2**: Nearly monophonic material

---

## Limitations

### 1. **Harmonic Material Only**

The algorithm assumes harmonic (tonal) material with clear harmonic series. It will **not work well** for:
- Inharmonic sounds (bells, drums, noise)
- Very short transients
- Dense spectral clutter

### 2. **Peak Assignment**

Each peak is assigned to only one voice. In cases where harmonics overlap (e.g., C4's 4th harmonic = C5's 2nd harmonic), only one voice gets the peak.

### 3. **Tuning Assumptions**

The note name calculation assumes 12-TET (equal temperament) with A4 = 440 Hz. Non-standard tunings will show incorrect note names (though frequencies are still correct).

### 4. **No Temporal Information**

This is a **spectral snapshot** analysis - it doesn't track when notes appear/disappear over time. For temporal tracking, you'd need to:
- Apply this to each time segment
- Track voice continuity across segments
- Handle voice onsets/offsets

---

## Future Integration Ideas

### Option 1: Voice-Separated Reconstruction

Add a new mode that reconstructs each voice independently:

```python
SPECTRAL_GROUP_BY_VOICE = True  # New option

# In spectral_concatenate():
if SPECTRAL_GROUP_BY_VOICE:
    voices = group_peaks_into_harmonic_series(peaks)
    for voice in voices:
        # Reconstruct this voice's harmonics
        # Create track group named "Voice_{note_name}"
```

**Benefits:**
- Separate mixer control per voice
- Individual voice processing
- Clear visual organization in DAW

### Option 2: Voice-Aware Partial Limits

Automatically adjust `SPECTRAL_MAX_PARTIALS` based on detected polyphony:

```python
voices = group_peaks_into_harmonic_series(peaks)
num_voices = len(voices)

# Allocate partials per voice
EFFECTIVE_MAX_PARTIALS = num_voices * 4  # 4 harmonics per voice
```

### Option 3: Chord Change Detection

Use voice analysis to detect chord changes:

```python
# Analyze each segment
voices_per_segment = []
for segment in segments:
    voices = group_peaks_into_harmonic_series(...)
    voices_per_segment.append(voices)

# Detect when chord voicing changes
# → Create new segment boundary
```

---

## Comparison to Existing Approach

### Current Spectral Reconstruction

```
Input: C Major Chord
↓
Extract ALL peaks (unsorted)
↓
Match top N peaks to corpus (e.g., 24 partials)
↓
Output: 24 tracks (mixed C/E/G harmonics)
```

**Result:** Combined spectral envelope, no voice separation

### With Harmonic Grouping

```
Input: C Major Chord
↓
Extract ALL peaks
↓
Group into harmonic series
↓
Identify: C4, E4, G4 (3 voices)
↓
Reconstruct each voice separately
↓
Output: 3 track groups (C harmonics, E harmonics, G harmonics)
```

**Result:** Voice-separated reconstruction, cleaner organization

---

## Related Files

- **Implementation:** `audioguide/spectralanalysis.py:279-386`
- **Test script:** `test_harmonic_grouping.py`
- **Test audio:**
  - `/Applications/AudioGuide/test_output/test_chord_c_major.wav`
  - `/Applications/AudioGuide/test_output/test_single_note_A4.wav`

---

## References

**Algorithm Inspiration:**
- YIN/PYIN pitch detection (harmonic template matching)
- MIREX Multiple F0 Estimation algorithms
- Classical additive synthesis (McAulay-Quatieri)

**Alternative Approaches:**
- Source separation (Spleeter, Demucs)
- Non-negative Matrix Factorization (NMF)
- Deep learning multi-f0 detection

---

## Next Steps

To integrate this into AudioGuide's main spectral reconstruction:

1. Add `SPECTRAL_GROUP_BY_VOICE` option to `defaults.py`
2. Modify `spectral_concatenate()` in `__init__.py` to:
   - Call `group_peaks_into_harmonic_series()` when enabled
   - Create separate reconstruction per voice
   - Generate track groups with voice labels
3. Test on real musical material (chord progressions, polyphonic melodies)
4. Compare output organization to ungrouped reconstruction

The function is **ready to use** - integration is straightforward when needed.
