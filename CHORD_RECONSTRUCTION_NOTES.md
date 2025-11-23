# Chord/Polyphonic Spectral Reconstruction

## Current Capability

The spectral reconstruction system **already supports chords** without modification! Here's why:

### How It Works:
1. **Spectral Analysis**: `extract_all_spectral_peaks()` finds ALL significant peaks in the spectrum
2. **No Harmonic Assumption**: Peaks are detected by amplitude, not harmonic relationships
3. **Frequency Matching**: Each peak is matched to the nearest corpus sine wave
4. **Layering**: All matched sines are stacked at the same time point

### For a Chord (e.g., C major: C4 + E4 + G4):
```
Target spectrum contains:
- C4 fundamental (261 Hz) + harmonics (522, 783, 1044...)
- E4 fundamental (330 Hz) + harmonics (660, 990, 1320...)
- G4 fundamental (392 Hz) + harmonics (784, 1176, 1568...)

Result: extract_all_spectral_peaks() finds ALL these frequencies
Reconstruction: Layers appropriate sine waves for the entire mixed spectrum
```

### Advantages:
✓ No source separation needed
✓ Works for any polyphonic content
✓ Reconstructs the combined spectral envelope
✓ Maintains relative amplitudes of all components

### Limitations:
- Doesn't identify which peaks belong to which "note"
- Can't separate voices or isolate individual chord tones
- Maximum partials limit (currently 4-16) may not capture full chord complexity

## Testing Chord Reconstruction

### Test 1: Simple Chord (Whole-File Mode)
```python
# Single sustained chord analyzed as one spectral snapshot
TARGET = tsf('chord_C_major.wav', thresh=-80)
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = True  # Analyze entire chord at once
SPECTRAL_MAX_PARTIALS = 24  # More partials for multiple fundamentals
```

### Test 2: Chord Progression (Segmented Mode)
```python
# Chord changes detected by onset detection
TARGET = tsf('chord_progression.wav', thresh=-35, offsetRise=0.05)
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False  # Segment at chord changes
SPECTRAL_MAX_PARTIALS = 24
```

## Future Enhancements

### 1. Harmonic Template Matching
- Identify which peaks form harmonic series
- Group peaks by fundamental frequency
- Enable per-note reconstruction from polyphonic material

### 2. Adaptive Partial Limits
- Automatically adjust `SPECTRAL_MAX_PARTIALS` based on polyphonic density
- More partials for chords, fewer for single notes

### 3. Spectral Masking Awareness
- Weight partials by perceptual importance
- Prioritize fundamentals over upper harmonics in dense textures

### 4. Voicing Separation
- Use source separation (e.g., Demucs, Spleeter) as preprocessor
- Analyze each voice separately
- Reconstruct with voice-specific controls

## Recommended Settings for Chords

```python
# Dense harmony (3+ notes)
SPECTRAL_MAX_PARTIALS = 24-32  # Capture multiple fundamentals + low harmonics
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.02  # 2% threshold to avoid noise

# Sparse harmony (2 notes)
SPECTRAL_MAX_PARTIALS = 12-16
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.01  # 1% threshold

# Single note
SPECTRAL_MAX_PARTIALS = 4-8
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.01
```

## Example: C Major Triad Reconstruction

Expected peaks (simplified, first 2 harmonics each):
1. C4 @ 261 Hz (fundamental)
2. C5 @ 522 Hz (2nd harmonic of C4)
3. E4 @ 330 Hz (fundamental)
4. E5 @ 660 Hz (2nd harmonic of E4)
5. G4 @ 392 Hz (fundamental)
6. G5 @ 784 Hz (2nd harmonic of G4)
   ...plus additional harmonics

With `SPECTRAL_MAX_PARTIALS = 24`, the system would capture most significant components of all three notes and reconstruct the full chord spectrum.
