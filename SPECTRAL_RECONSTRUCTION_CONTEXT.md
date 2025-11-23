# AudioGuide Spectral Reconstruction Implementation

## Current Status: FULLY OPERATIONAL ✓

**Last Updated:** 2025-11-14

## Overview

Spectral reconstruction synthesis has been successfully integrated into AudioGuide. This mode reconstructs pitched sounds by matching corpus samples to individual harmonics of the target, rather than matching overall timbre.

## Test Results

### Successful Test Run (2025-11-14)
- **Configuration:** `examples/cello_sines_spectral.py`
- **Target:** Melodic cello phrase (Staub-MelodicCello.wav)
- **Corpus:** 118 pure sine waves (Serum_Sine_Short/)
- **Output:**
  - 118 tracks (one per unique frequency)
  - 517 layered events (~4.4 events per track)
  - Successfully generated RPP (229K), CSD (142K), and WAV (4.9M)

## Implementation Details

### 1. Core System Files

#### `/audioguide/__init__.py` (lines 71-77, 342-467)
- Modified `execute()` to choose concatenation mode based on `USE_SPECTRAL_RECONSTRUCTION`
- Added `spectral_concatenate()` method for spectral processing
- Creates custom `SpectralEvent` class with all required output methods:
  - `makeDictOutput()` - JSON output
  - `makeMaxMspListOutput()` - Max/MSP format
  - `makeLabelText()` - Label file format
  - `makeLispText()` - Lisp format
  - `makeCsoundOutputText()` - Csound score format

#### `/audioguide/defaults.py` (lines 108-112)
```python
USE_SPECTRAL_RECONSTRUCTION = False
SPECTRAL_TOLERANCE_CENTS = 50
SPECTRAL_MAX_PARTIALS = 8
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.01
```

#### `/audioguide/tests.py` (lines 197-201, 312-315)
- Registered spectral options in validation system
- Categorized as "concate" options

#### `/audioguide/spectrallayering.py`
Core spectral matching algorithm:
- `spectral_layering_match()` - Main matching function
- `find_corpus_by_frequency()` - Finds corpus by natural frequency (NO transposition)
- `compute_gain_adjustment()` - Calculates gain in dB to match target amplitude
- `compute_gain_envelope()` - Time-varying gain envelope (stored, not yet applied to tracks)

#### `/audioguide/spectralanalysis.py`
Harmonic extraction via FFT:
- `analyze_segment_spectrum()` - Extracts fundamental + harmonics
- `find_peaks_parabolic()` - Peak detection with parabolic interpolation
- `estimate_f0_from_harmonics()` - Fundamental frequency estimation

#### `/audioguide/fileoutput/reaper.py`
- Modified to use VOLPAN (clip gain) instead of TAKEENV for compatibility
- Multiplies gain directly into VOLPAN parameter
- Stores `gain_envelope` data for future VOLUMEENV implementation

### 2. How It Works

1. **Harmonic Extraction:**
   - Loads target audio segment via soundfile
   - Performs FFT analysis to extract fundamental + up to 16 harmonics
   - Tracks amplitude envelope for each partial

2. **Frequency Matching:**
   - For each target harmonic, finds corpus sounds with matching f0
   - Uses tolerance of 50 cents (configurable)
   - Selects corpus by natural frequency - NO pitch transposition

3. **Gain Calculation:**
   - Computes gain adjustment in dB to match target partial amplitude
   - Generates time-varying gain envelope (stored but not yet applied)
   - Clamps gain to reasonable range (-60 to +24 dB)

4. **Event Generation:**
   - Creates SpectralEvent objects with all required attributes
   - MIDI pitch calculated from matched target frequency
   - NO transposition (transposition = 0.0, transratio = 1.0)
   - Duration matches target segment duration

5. **Output Rendering:**
   - Generates Reaper RPP with one track per unique corpus frequency
   - Multiple events per track when same frequency reused
   - Static VOLPAN gain applied (gain envelope stored for future use)
   - Also generates Csound and renders to WAV

## Configuration Parameters

### `USE_SPECTRAL_RECONSTRUCTION` (boolean)
- `False` (default) - Standard descriptor-based matching
- `True` - Spectral reconstruction mode

### `SPECTRAL_TOLERANCE_CENTS` (float)
- Default: 50 cents (quarter tone)
- How close corpus f0 must be to target partial frequency
- Lower = stricter matching, fewer matches found
- Higher = looser matching, more candidates

### `SPECTRAL_MAX_PARTIALS` (int)
- Default: 8
- Maximum number of harmonics to match per target segment
- Lower harmonics prioritized (fundamental, 2nd, 3rd, etc.)

### `SPECTRAL_MIN_AMPLITUDE_RATIO` (float)
- Default: 0.01 (1% of loudest partial)
- Minimum partial amplitude to include
- Filters out very quiet partials

## Key Technical Decisions

### 1. Direct Audio Loading
**Problem:** AnalInterface doesn't have `getSegmentAudio()` method
**Solution:** Load audio directly using soundfile library
```python
audio_data, sr = sf.read(target_segment.filename)
start_sample = int(target_segment.segmentStartSec * sr)
end_sample = int((target_segment.segmentStartSec + target_segment.segmentDurationSec) * sr)
target_audio = audio_data[start_sample:end_sample]
```

### 2. Custom Event Class
**Problem:** `outputEvent` constructor requires 11 complex arguments not available in spectral mode
**Solution:** Created custom `SpectralEvent` class with minimal required attributes set directly
```python
class SpectralEvent:
    def makeDictOutput(self): ...
    def makeMaxMspListOutput(self): ...
    def makeLabelText(self): ...
    def makeLispText(self): ...
    def makeCsoundOutputText(self, channelMethod, instru=1): ...
```

### 3. VOLPAN Instead of TAKEENV
**Problem:** TAKEENV not supported in older Reaper versions
**Solution:** Multiply gain directly into VOLPAN (universal clip gain)
```python
final_volume = d['ampscale']
if has_envelope:
    _, gain_db = d['gain_envelope'][0]
    gain_linear = db_to_linear(gain_db)
    final_volume = d['ampscale'] * gain_linear
```

### 4. Gain Envelope Storage
**Decision:** Store time-varying gain envelope in event for future use
**Status:** Data stored, not yet applied as track VOLUMEENV automation
**Next Step:** Implement track-level volume envelope in Reaper output

## Known Limitations

1. **No Time-Varying Gain Yet:**
   - Gain envelopes computed but not applied as track automation
   - Currently using static VOLPAN gain from first envelope point
   - Need to implement VOLUMEENV track automation in reaper.py

2. **Librosa Dependency:**
   - Warning message about missing librosa (PYIN pitch detection)
   - Not critical - spectral analysis uses scipy FFT instead
   - User notes: "librosa may only run on python 3.7 or 3.8 on my m1 machine"

3. **Single Target Segment Processing:**
   - Processes each target segment independently
   - No cross-segment optimization or voice leading
   - Could benefit from analyzing spectral evolution across segments

## Testing Configuration

### Minimal Test: `examples/cello_sines_spectral.py`
```python
TARGET = tsf('/Users/.../Staub-MelodicCello.wav', thresh=-30, offsetRise=0.01)
CORPUS = [csf('/Users/.../Serum_Sine_Short', wholeFile=True)]

USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_TOLERANCE_CENTS = 50
SPECTRAL_MAX_PARTIALS = 8
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.01

SEARCH = [spass('closest', d('f0-seg', norm=1))]
SUPERIMPOSE = si(maxSegment=16, maxOverlap=16)
ENABLE_TAKEENV = False

RPP_FILEPATH = '/Applications/AudioGuide/test_output/cello_spectral.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/cello_spectral.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/cello_spectral_log.html'
```

## Next Steps

### 1. Audio Quality Evaluation
- [ ] Listen to rendered output (cello_spectral.wav)
- [ ] Assess spectral reconstruction quality
- [ ] Compare to original target
- [ ] Identify artifacts or missing partials

### 2. Parameter Optimization
- [ ] Test different SPECTRAL_TOLERANCE_CENTS values
- [ ] Experiment with SPECTRAL_MAX_PARTIALS
- [ ] Adjust SPECTRAL_MIN_AMPLITUDE_RATIO
- [ ] Find optimal balance between accuracy and corpus coverage

### 3. Time-Varying Gain Implementation
- [ ] Add VOLUMEENV track automation to reaper.py
- [ ] Use stored gain_envelope data
- [ ] Test dynamic amplitude matching
- [ ] Compare static vs. dynamic gain

### 4. Algorithm Refinements
- [ ] Implement partial masking (don't match partials already covered)
- [ ] Add voice leading across segments
- [ ] Optimize corpus selection when multiple candidates available
- [ ] Consider phase alignment between partials

### 5. Additional Testing
- [ ] Test with different targets (voice, instruments)
- [ ] Test with richer corpus (filtered noise, complex tones)
- [ ] Test with polyphonic targets
- [ ] Stress test with large corpus and long targets

## Error History & Solutions

### Integration Errors (Fixed)
1. **Missing instruments attribute** - Added instruments initialization in spectral_concatenate
2. **Missing event attributes (midi, etc.)** - Added all required attributes to SpectralEvent
3. **Missing output methods** - Implemented makeDictOutput, makeMaxMspListOutput, makeLabelText, makeLispText, makeCsoundOutputText
4. **Type mismatch (classification)** - Changed from string ('') to integer (0)
5. **Indentation errors** - Fixed Python class method indentation

## File References

### Modified Files
- `/audioguide/__init__.py` - Main execution logic
- `/audioguide/defaults.py` - Configuration options
- `/audioguide/tests.py` - Option validation
- `/audioguide/fileoutput/reaper.py` - RPP output with VOLPAN

### New Files
- `/audioguide/spectrallayering.py` - Spectral matching algorithm
- `/audioguide/spectralanalysis.py` - Harmonic extraction
- `/examples/cello_sines_spectral.py` - Test configuration

### Output Files (Test)
- `/Applications/AudioGuide/test_output/cello_spectral.rpp` (229K)
- `/Applications/AudioGuide/test_output/cello_spectral.csd` (142K)
- `/Applications/AudioGuide/test_output/cello_spectral.wav` (4.9M)
- `/Applications/AudioGuide/test_output/spectral_run*.log` (debug logs)

## Usage Example

```python
from audioguide import audioguide

# Configure spectral reconstruction
options = {
    'USE_SPECTRAL_RECONSTRUCTION': True,
    'SPECTRAL_TOLERANCE_CENTS': 50,
    'SPECTRAL_MAX_PARTIALS': 8,
    'SPECTRAL_MIN_AMPLITUDE_RATIO': 0.01,
    'TARGET': tsf('target.wav'),
    'CORPUS': [csf('sine_waves/')],
    'RPP_FILEPATH': 'output.rpp'
}

# Execute
ag = audioguide(**options)
ag.execute()
```

## Performance Notes

- Analysis phase: Fast (FFT-based harmonic extraction)
- Matching phase: O(target_segments × corpus_segments × max_partials)
- Output generation: Fast (standard AudioGuide pipeline)
- Bottleneck: Corpus frequency matching for large corpora

## Contact & Support

For questions or issues with spectral reconstruction:
1. Check this context file for known limitations
2. Review test logs in `/Applications/AudioGuide/test_output/`
3. Examine generated RPP file structure
4. Test with minimal corpus first

---

**Implementation Status:** ✓ Complete and operational
**Last Test:** 2025-11-14 01:10 AM - SUCCESS
**Next Milestone:** Time-varying VOLUMEENV implementation
