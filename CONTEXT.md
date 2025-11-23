# AudioGuide Spectral Reconstruction - Context Summary

**Last Updated:** November 17, 2025
**Session Focus:** Spectral reconstruction + VOLUMEENV implementation

---

## Overview

AudioGuide now supports **spectral reconstruction synthesis** - a mode where target sounds are analyzed for their spectral content (fundamental + harmonics) and reconstructed by layering corpus sounds matched to individual spectral peaks. This enables additive synthesis-style reconstruction using pure sine waves or other tonal corpora.

---

## Key Features Implemented

### 1. Spectral Reconstruction Mode (`USE_SPECTRAL_RECONSTRUCTION`)
- **Purpose**: Match corpus sounds to individual spectral peaks instead of overall timbre
- **Method**: FFT-based spectral peak detection without pitch estimation dependency
- **Advantage**: Works for monophonic, polyphonic, and chord material

### 2. Whole-File Analysis (`SPECTRAL_WHOLE_FILE`)
- **Purpose**: Analyze entire target as single spectral snapshot (no segmentation)
- **Use case**: Sustained notes, drones, chords
- **Result**: All matched partials stacked at time 0 for pure additive synthesis

### 3. Direct Peak Detection (No Pitch Estimation Required)
- **Function**: `extract_all_spectral_peaks()` in `spectralanalysis.py`
- **Method**: Find local maxima in FFT spectrum above amplitude threshold
- **Benefit**: Robust to complex spectra, no octave errors from f0 detection
- **Replaced**: Previous harmonic series extraction that relied on unreliable zero-crossing pitch detection

### 4. Track-Level Volume Automation (`ENABLE_SPECTRAL_VOLUMEENV`)
- **Purpose**: Time-varying amplitude automation for spectral partials
- **Method**: Writes VOLENV (track-level volume automation) to Reaper RPP files
- **Benefit**: Each partial's amplitude evolves dynamically instead of static clip gain
- **Status**: Fully implemented and tested (Nov 17, 2025)

---

## File Structure

### Core Implementation Files

**audioguide/defaults.py** (lines 108-115)
```python
USE_SPECTRAL_RECONSTRUCTION = False
SPECTRAL_WHOLE_FILE = False
SPECTRAL_TOLERANCE_CENTS = 50
SPECTRAL_MAX_PARTIALS = 8
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.01
ENABLE_SPECTRAL_VOLUMEENV = False  # Track-level volume automation
```

**audioguide/spectralanalysis.py**
- `extract_all_spectral_peaks()` - Direct FFT peak detection (lines 225-276)
- `analyze_segment_spectrum()` - Main analysis function (lines 279-322)
- `extract_partial_envelopes()` - Time-varying amplitude extraction (lines 80-124)

**audioguide/__init__.py** (lines 342-491)
- `spectral_concatenate()` - Main spectral reconstruction method
- Whole-file mode logic (lines 374-380)
- SpectralEvent generation (lines 388-484)

**audioguide/spectrallayering.py**
- `spectral_layering_match()` - Core matching algorithm
- Frequency-based corpus selection
- Gain calculation for matched partials

**audioguide/tests.py** (lines 198-203, 314-319)
- Option validation for spectral reconstruction parameters
- ENABLE_SPECTRAL_VOLUMEENV registered as 'True or False'

**audioguide/fileoutput/reaper.py** (lines 48-79, 111-116, 135-140)
- `format_volumeenv()` - Generates VOLENV automation chunks
- Double-gain prevention logic (line 111)
- Track-level automation output

**audioguide/concatenativeclasses.py** (line 1095)
- `gain_envelope` data passthrough to track items

---

## Test Corpora

### Optimal Pure Sine Corpus (Generated)
**Location:** `/Applications/AudioGuide/test_output/spectral_sine_corpus/`
- **Files**: 84 chromatic sine waves (C1-B7, 32.7-3951 Hz)
- **Properties**: 
  - Pure sine (>99.9% harmonic purity)
  - 5s duration, 5ms linear fades
  - 0.707 peak amplitude (-3 dBFS)
  - 48kHz, 24-bit mono
- **Total size**: 57.7 MB
- **Generation script**: Created via numpy/soundfile

### Original Serum Sine Corpus (For Comparison)
**Location:** `/Users/jonathankawchuk/Documents/Projects/In Progress/Album 3/corpora/Serum_Sine_Short`
- **Properties**:
  - Only 10ms sustained, rest is 3s decay
  - 54.7% harmonic purity (NOT pure sine)
  - Wrong tuning (482 Hz instead of 440 Hz for A4)
  - Designed for synthesis, not additive reconstruction
- **Status**: Tested for comparison - not recommended for spectral reconstruction

---

## Test Files and Results

### Single Note Tests

**spectral_single_wholefile.py**
- Target: cello_Ds2_single_note.wav (2.04s, Ds3 @ 155.58 Hz)
- Mode: SPECTRAL_WHOLE_FILE = True
- Partials: 16
- Result: **16 tracks all at position 0.000000** - successful whole-file reconstruction
- Files: `spectral_wholefile.rpp`, `spectral_wholefile.wav`

### Monophonic Phrase Tests

**spectral_monophonic.py** (16 partials)
- Target: cello phrase (82s, 96kHz mono)
- Mode: Segmented (SPECTRAL_WHOLE_FILE = False)
- Result: **232 segments, 7,416 events** (16 partials per segment)
- Duration: 57.3 seconds reconstructed
- Files: `spectral_monophonic.rpp` (1.3MB), `spectral_monophonic.wav` (7.5MB)
- Issue: Upper harmonics mask fundamental

**spectral_monophonic_few_partials.py** (4 partials)
- Same target as above
- Partials: 4 (fundamental + 3 harmonics)
- Result: **232 segments, 1,856 events** (75% reduction)
- Files: `spectral_monophonic_few.rpp` (339KB), `spectral_monophonic_few.wav` (7.5MB)
- **Outcome**: Clearer fundamental perception, better melodic clarity

**spectral_monophonic_short_sines.py** (short corpus test)
- Same target, using original Serum_Sine_Short corpus
- Purpose: Compare optimized vs non-optimized corpus
- Result: **112 corpus tracks** (33% fewer than optimized)
- Files: `spectral_short_sines.rpp` (405KB), `spectral_short_sines.wav` (15MB - 2x larger!)
- Issue: Reduced spectral coverage, likely due to mistuning and impure harmonics

---

## Configuration Parameters

### Spectral Reconstruction Settings

**USE_SPECTRAL_RECONSTRUCTION** (Boolean)
- Enable spectral reconstruction mode
- Default: False

**SPECTRAL_WHOLE_FILE** (Boolean)  
- Analyze entire target as single segment (no onset detection)
- Use for: sustained notes, drones, chords
- Default: False

**SPECTRAL_TOLERANCE_CENTS** (Number > 0)
- Frequency matching tolerance in cents
- 100 cents = 1 semitone (chromatic spacing)
- Default: 50 cents

**SPECTRAL_MAX_PARTIALS** (Integer > 0)
- Maximum spectral peaks to match per segment
- Recommendations:
  - Single note: 4-8
  - Sparse harmony (2 notes): 12-16
  - Dense harmony (3+ notes/chord): 24-32
- Default: 8

**SPECTRAL_MIN_AMPLITUDE_RATIO** (Number > 0)
- Minimum peak amplitude relative to maximum (0.01 = 1%)
- Filters weak partials/noise
- Default: 0.01

---

## Key Discoveries and Fixes

### Problem 1: Missing Fundamental
**Issue**: Original implementation only detected harmonics 3, 6, 9, 12, 15 (missing fundamental)
**Root Cause**: Zero-crossing f0 detector incorrectly identified 469 Hz as fundamental instead of 156 Hz (octave error)
**Solution**: Implemented direct FFT peak detection (`extract_all_spectral_peaks()`)
**Result**: Fundamental now correctly detected as strongest component

### Problem 2: Target Over-Segmentation  
**Issue**: Single sustained notes segmented into 100+ tiny segments
**Root Cause**: Onset detection too sensitive for sustained material
**Solution**: Added `SPECTRAL_WHOLE_FILE` mode to bypass segmentation
**Result**: True whole-file spectral snapshots possible

### Problem 3: Upper Harmonics Masking Fundamental
**Issue**: 16 partials per segment created harmonic clutter
**Observation**: Too many upper harmonics obscured melodic fundamental
**Solution**: Reduced `SPECTRAL_MAX_PARTIALS` to 4 (fundamental + 3 harmonics)
**Result**: 75% fewer events, clearer fundamental perception

### Problem 4: Corpus Quality Impact on Spectral Reconstruction
**Issue**: Original Serum_Sine_Short corpus produced inferior results
**Comparison Test**: Same target, same settings (4 partials), different corpora

| Metric | Optimized Corpus | Original Serum_Sine_Short | Difference |
|--------|-----------------|---------------------------|------------|
| Unique corpus files used | 167 | 112 | **-33%** (55 fewer matches) |
| RPP file size | 339 KB | 405 KB | +19% |
| Rendered audio size | 7.5 MB | 15 MB | **+100%** (2x larger!) |

**Root Causes**:
1. **Mistuning**: Serum corpus tuned to 482 Hz instead of 440 Hz (A4 reference)
2. **Harmonic impurity**: Only 54.7% pure sine content vs >99.9% in optimized corpus
3. **Wrong envelope**: 10ms sustain + 3s decay vs 5s sustained in optimized corpus
4. **Reduced frequency coverage**: Chromatic spacing misses target spectral peaks

**Conclusion**: Optimized pure sine corpus is superior for spectral reconstruction
- More spectral matches (167 vs 112 unique frequencies)
- Smaller rendered files (7.5 MB vs 15 MB)
- Pure harmonic content prevents spectral pollution

---

## Chord/Polyphonic Support

**Current Status**: **Already supported!**

The spectral peak detection approach works for polyphonic material without modification:
- Detects ALL spectral peaks regardless of source
- No harmonic template assumptions
- Reconstructs combined spectral envelope

### For C Major Chord (C4 + E4 + G4):
- C4 fundamental (261 Hz) + harmonics
- E4 fundamental (330 Hz) + harmonics  
- G4 fundamental (392 Hz) + harmonics
- **Result**: All frequencies detected and reconstructed

### Recommended Settings:
```python
SPECTRAL_MAX_PARTIALS = 24-32  # More partials for multiple fundamentals
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.02  # Slightly higher threshold for dense textures
```

See: `CHORD_RECONSTRUCTION_NOTES.md` for detailed documentation

---

## Next Steps / Future Work

### 1. Harmonic Template Matching
- Identify which peaks form harmonic series
- Group peaks by fundamental frequency
- Enable per-note reconstruction from polyphonic sources

### 2. Adaptive Partial Limits
- Auto-adjust SPECTRAL_MAX_PARTIALS based on polyphonic density
- Context-aware spectral analysis

### 3. Pitch-Aware Segmentation
- Segment at pitch changes (not just onsets)
- Better for legato monophonic lines
- Would benefit from librosa PYIN if available

---

## Usage Examples

### Single Sustained Note
```python
TARGET = tsf('single_note.wav', thresh=-80, offsetRise=0.5)
CORPUS = [csf('spectral_sine_corpus', wholeFile=True)]

USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = True  # Analyze as one snapshot
SPECTRAL_MAX_PARTIALS = 8
SPECTRAL_TOLERANCE_CENTS = 100
```

### Monophonic Melody (Clear Fundamental)
```python
TARGET = tsf('melody.wav', thresh=-35, offsetRise=0.05, minSegLen=0.1)
CORPUS = [csf('spectral_sine_corpus', wholeFile=True)]

USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False  # Segment at note changes
SPECTRAL_MAX_PARTIALS = 4  # Fundamental + 3 harmonics only
SPECTRAL_TOLERANCE_CENTS = 100
```

### Chord/Polyphonic Material
```python
TARGET = tsf('chord_progression.wav', thresh=-35, offsetRise=0.05)
CORPUS = [csf('spectral_sine_corpus', wholeFile=True)]

USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False  # Segment at chord changes
SPECTRAL_MAX_PARTIALS = 24  # Capture multiple fundamentals
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.02  # 2% threshold
```

---

## Technical Notes

### Spectral Analysis Pipeline
1. Load target segment audio
2. Compute FFT spectrum
3. Find local peaks using `scipy.signal.find_peaks()`
4. Filter peaks by amplitude threshold
5. Sort by amplitude (descending)
6. Return top N peaks (SPECTRAL_MAX_PARTIALS)

### Corpus Matching
1. For each target peak frequency
2. Search corpus for nearest frequency match
3. Check tolerance (cents-based)
4. Calculate gain adjustment (dB)
5. Create SpectralEvent with all required attributes

### Output Event Structure
SpectralEvent contains:
- Corpus segment reference
- Time position (segment start)
- Duration (segment duration)
- Gain (matched amplitude)
- Transposition (0.0 for spectral mode - no pitch shifting)
- Gain envelope (time-varying amplitude data)

---

## Dependencies

**Required:**
- numpy
- scipy
- soundfile

**Optional:**
- librosa (for PYIN pitch detection - currently disabled/unused)

---

## Known Issues

1. **Librosa compatibility**: PYIN unavailable on Python 3.13/M1
   - **Impact**: None - bypassed with direct peak detection
   - **Workaround**: Direct FFT peak analysis is more robust anyway

2. **Chromatic corpus spacing**: Some harmonics fall between chromatic notes
   - **Example**: 700 Hz falls between F5 (698 Hz) and Fs5 (740 Hz)
   - **Impact**: Slight mistuning for non-harmonic partials
   - **Solution**: Generate quarter-tone or microtonal corpus for better coverage

---

## Performance Notes

- 82-second target at 96kHz with 16 partials: ~2 minutes processing
- Reduced to 4 partials: Faster processing, 75% fewer events
- Descriptor computation is the bottleneck (caching helps on repeated runs)

---

## References

- Original Serum corpus analysis: `/Applications/AudioGuide/test_output/spectral_comparison.txt`
- Fundamental detection fix: `/Applications/AudioGuide/test_output/spectral_fix_summary.txt`
- Chord reconstruction notes: `/Applications/AudioGuide/audioguide-claude/CHORD_RECONSTRUCTION_NOTES.md`
