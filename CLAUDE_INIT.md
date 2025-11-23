# AudioGuide - Claude Context & Improvement Plan

> **Quick Start for New Claude Sessions**: Read "Executive Summary" below, then jump to relevant sections as needed. Full technical details follow.

---

## Executive Summary (Start Here!)

### What This Is

**AudioGuide** is a non-realtime concatenative synthesis system (Python, v1.79) that reconstructs target sounds using corpus samples matched by audio descriptors.

**Current problem**: Excellent at timbre matching, **awful** at creating harmonic, tonal, melodic content.

**Our goal**: Add **spectral reconstruction synthesis** - recreate target sounds by layering corpus sounds to match individual harmonics, with time-varying amplitude control.

### Key Decisions Made (User Preferences)

1. ✅ **No transposition by default** - Only position and gain changes to corpus audio
2. ✅ **If transposition needed**: Varispeeding (playback rate), NOT algorithmic pitch shifting
3. ✅ **Implication**: Spectral layering must match corpus by natural frequency (no pitch shifting)
4. ✅ **Segmentation**: Optional FluCoMa novelty slice for whole-file feel
5. ✅ **F0 analysis**: Upgrade to PYIN (better than current YIN)

### Critical Technical Findings

1. **TAKEENV not VOLUMEENV!**
   - Item-level volume automation (clip gain) uses `<TAKEENV>` inside `<TAKE>` chunk
   - Structure: `ITEM > TAKE > TAKEENV > PT` (automation points)
   - VOLUMEENV = track-level (post-FX) - wrong for our needs

2. **Python libraries evaluated**:
   - reapy: Requires running Reaper (dealbreaker)
   - reathon: No TAKEENV support, but extensible
   - **Decision**: Extend AudioGuide's existing `reaper.py` (47 lines)

3. **Tool assessment**:
   - ❌ FluCoMa for descriptor replacement (wrong focus)
   - ✅ FluCoMa for optional segmentation (good idea)
   - ✅ PYIN for F0 tracking (upgrade from YIN)

### Immediate Next Steps

**Phase 1: Proof of Concept Test** (See `GROK_PROMPT_CELLO_TEST.md`)
- Generate sine corpus (65-2000 Hz)
- Manually reconstruct cello from sines
- Validate TAKEENV format in Reaper
- **Status**: Ready for Grok to execute

**Phase 2: Implementation** (After proof-of-concept succeeds)
1. Add harmonic series extraction (`spectralanalysis.py`)
2. Implement spectral layering algorithm (`spectrallayering.py`)
3. Extend `.rpp` export with TAKE/TAKEENV support
4. Add PYIN f0 tracking
5. Optional: FluCoMa segmentation wrapper

### Where to Find Details

- **Architecture overview**: "Project Overview" section below
- **Current limitations**: "Current Capabilities" section
- **Pitch/harmonic improvements**: "DETAILED APPROACH: Improving Pitch and Harmonic Analysis" section (6 layers)
- **RPP export details**: "Enhanced .RPP Export with Clip Gain Automation" section
- **Test case**: "Validation Test Case: Cello from Sine Tones" section
- **Questions to resolve**: "Questions to Resolve Before Implementation" section
- **User preferences**: "User Preference Clarifications" section at end

### Files Referenced

- Current RPP export: `audioguide/fileoutput/reaper.py` (47 lines)
- Segmentation: `audioguide/sfsegment.py`
- Descriptors: `audioguide/descriptordata.py`
- Similarity: `audioguide/simcalc.py`
- Partial analysis: `audioguide/partialanalysis.py` (experimental)
- Examples: `/Applications/AudioGuide/audioguide/examples/`

### Key Insight

**This is additive synthesis via concatenative synthesis** - reconstructing sounds by layering simple building blocks (corpus sounds) to match the spectral composition of complex targets. The cello-from-sines test validates this approach.

---

## Project Overview

**AudioGuide** is a sophisticated non-realtime concatenative synthesis system written in Python by Ben Hackbarth, Norbert Schnell, Philippe Esling, and Diemo Schwarz (version 1.79).

### What AudioGuide Does

AudioGuide performs intelligent concatenative synthesis by:
1. Analyzing a "target" audio file and segmenting it into discrete sound units
2. Analyzing a "corpus" of audio files (the sound palette)
3. Matching corpus sounds to target segments based on audio descriptors (timbre, duration, pitch, etc.)
4. Creating dense, layered concatenations by superimposing multiple corpus sounds
5. Exporting results to various DAW formats (Csound, Reaper, Logic/Pro Tools)

### Key Architecture

```
/Applications/AudioGuide/audioguide/
├── agConcatenate.py              # Main entry point
├── audioguide/                   # Core module
│   ├── __init__.py               # Main API and execution flow
│   ├── concatenativeclasses.py  # Core concatenation logic
│   ├── sfsegment.py              # Sound file segmentation
│   ├── descriptordata.py         # Audio descriptor management
│   ├── anallinkage.py            # Audio analysis interface (IRCAM)
│   ├── simcalc.py                # Similarity calculations
│   ├── partialanalysis.py        # Partial/harmonic analysis (experimental)
│   └── fileoutput/
│       ├── reaper.py             # Reaper .rpp export
│       ├── aaf.py                # AAF (Logic/Pro Tools)
│       └── csoundinterface.py    # Csound rendering
```

---

## Current Capabilities

### Strengths (Timbre Matching)

AudioGuide excels at timbral matching:
- **Comprehensive spectral descriptors**: centroid, spread, skewness, kurtosis, slope, rolloff, flatness, crest
- **MFCCs (0-12)**: Excellent for timbral texture
- **Harmonic descriptors**: harmonic energy, centroid, deviation, odd/even ratio, inharmonicity
- **Perceptually weighted features**: psychoacoustic scaling
- **Multiple distance metrics**: Euclidean, correlation, KL-divergence, DTW
- **Flexible search**: Multi-pass filtering, weighted combinations, normalization

### Weaknesses (Pitched Content)

AudioGuide is **awful** at creating harmonic, tonal, melodic content:

1. **Limited pitch tracking**:
   - Uses YIN f0 detection (200-1000 Hz default range)
   - No polyphonic pitch detection
   - Simple median-based pitch estimation

2. **No harmonic/melodic context**:
   - No pitch contour analysis (can't match rising/falling melodies)
   - No interval analysis (doesn't understand melodic relationships)
   - No key/scale awareness (can't match tonal context)
   - No harmonic progression matching (treats each frame independently)

3. **Chroma features underutilized**:
   - Available (chroma0-11) but not prominently used
   - No pitch class set analysis or tonal distance metrics

4. **Partial analysis is experimental**:
   - Located in `partialanalysis.py`
   - Marked as "experimental, untested, and undocumented"
   - Only matches pitch and amplitude, not harmonic relationships

5. **No spectral layering strategy**:
   - Cannot recreate the spectral composition of a target by layering multiple corpus sounds
   - No volume/amplitude adjustment to match harmonic series
   - No consideration of partial frequencies when selecting corpus sounds

---

## Current .RPP Export Implementation

### Location
- Main file: `/Applications/AudioGuide/audioguide/audioguide/fileoutput/reaper.py` (47 lines)
- Invocation: `/Applications/AudioGuide/audioguide/audioguide/__init__.py:413-423`
- Track organization: `/Applications/AudioGuide/audioguide/audioguide/concatenativeclasses.py:1040-1100`

### Current Features

**Per-Item (Audio Clip)**:
- Position in timeline (seconds)
- Clip name
- Duration
- Source file offset (SOFFS)
- Volume/pan settings (amplitude scaling) - **STATIC ONLY**
- Fade in/out durations
- Playback rate (for transposition)
- Source file path

**Per-Track**:
- Track name (derived from corpus file or "target")
- Multiple audio items organized to avoid overlaps

### Current Data Structure

Each audio clip is represented as:
```python
{
    'file': filepath,
    'name': printName,
    'time': timeInScore,              # Start position
    'stop': timeInScore+duration,     # End position
    'skip': sfSkip,                   # Offset into source file
    'duration': duration,
    'amp': amplitude,                 # STATIC amplitude value
    'ampscale': dbToAmp(envDb),      # STATIC amplitude scaling
    'fadein': envAttackSec,
    'fadeout': envDecaySec,
    'transposition': semitones
}
```

### Critical Limitations

1. **No clip gain automation**:
   - Only static `VOLPAN` value per clip
   - Cannot vary volume over time within a clip
   - No automation envelopes for amplitude

2. **No track-level features**:
   - No FX chains, sends, or automation
   - Missing pan, volume, mute, solo at track level

3. **Limited routing**:
   - No track routing, sends, or busing

4. **No parameter automation**:
   - No automation envelopes for any parameter
   - Critical for spectral reconstruction approach

---

## IMPROVEMENT PLAN: Spectral Reconstruction Concatenative Synthesis

### Core Concept

Transform AudioGuide from **timbre-matching** to **spectral-reconstruction** synthesis:

Instead of matching whole sounds by timbre, **recreate the spectral and melodic feeling of a target by layering whole-file corpus sounds, adjusting their volumes to match the harmonic series**.

#### Analogy
- **Target sound**: Made of many sine tones at different volumes (fundamental + harmonics)
- **Improved AudioGuide**: Recreate by layering corpus sounds, adjusting volume to match spectral composition

### Key Improvements Needed

#### 1. Enhanced Spectral Analysis

**File to modify**: `audioguide/anallinkage.py`, `audioguide/descriptordata.py`

**Add**:
- **Spectral decomposition** per segment:
  - Extract fundamental frequency and all harmonics (using FFT or sinusoidal modeling)
  - Store amplitude of each harmonic (dB or linear)
  - Store frequency of each partial (for inharmonic sounds)

- **Harmonic template extraction**:
  - Create a "spectral fingerprint" for each segment
  - Store as array: `[(freq1, amp1), (freq2, amp2), ...]`

- **Melodic contour descriptors**:
  - Pitch trajectory over time (not just median)
  - Pitch slope, vibrato rate/depth
  - Interval relationships between adjacent segments

#### 2. Corpus Sound Pitch/Spectral Indexing

**File to modify**: `audioguide/descriptordata.py`, `audioguide/concatenativeclasses.py`

**Add**:
- **Dominant pitch extraction** for each corpus sound:
  - Use improved `f0SegV2()` or integrate sinusoidal analysis
  - Store fundamental frequency + first N harmonics

- **Spectral centroid** for each corpus sound (already exists but needs prominence)

- **Harmonic richness metrics**:
  - Number of strong partials
  - Harmonic vs. inharmonic energy ratio

#### 3. Spectral Layering Algorithm

**File to create**: `audioguide/spectrallayering.py`

**New matching strategy**:

For each target segment:
1. **Extract spectral composition**:
   - Get fundamental frequency and all harmonics with amplitudes

2. **Select corpus sounds to recreate each partial**:
   - For each strong partial in target:
     - Find corpus sounds whose fundamental matches that partial frequency (within tolerance)
     - Consider transposition to match exact frequency
     - Score by spectral similarity

3. **Compute volume adjustments**:
   - For each selected corpus sound, compute `clip_gain` to match target partial amplitude
   - Store as time-varying value (automation envelope)

4. **Layer sounds**:
   - Superimpose multiple corpus sounds per target segment
   - Each represents a different partial/harmonic
   - Volume automation matches target spectral evolution

**Pseudocode**:
```python
def spectral_layering_match(target_segment, corpus):
    # Extract target spectral composition
    target_partials = extract_harmonic_series(target_segment)
    # [(freq1, amp1, time_varying_amp[]), (freq2, amp2, time_varying_amp[]), ...]

    selected_sounds = []

    for partial_freq, partial_amp, partial_amp_envelope in target_partials:
        # Find corpus sound whose fundamental matches this partial
        candidates = find_corpus_by_pitch(corpus, partial_freq, tolerance_cents=50)

        # Score by spectral similarity
        best_match = score_and_select(candidates, target_segment, weight_by='spectral_centroid')

        # Compute clip gain to match partial amplitude
        clip_gain_envelope = compute_gain_envelope(best_match, partial_amp_envelope)

        selected_sounds.append({
            'corpus_sound': best_match,
            'transposition': freq_to_semitones(partial_freq / best_match.f0),
            'clip_gain_envelope': clip_gain_envelope  # TIME-VARYING
        })

    return selected_sounds
```

#### 4. Improved Harmonic Analysis

**File to improve**: `audioguide/partialanalysis.py`, `audioguide/simcalc.py`

**Elevate partial analysis from "experimental" to core**:
- Improve sinusoidal modeling accuracy
- Add polyphonic pitch detection (e.g., using PYIN or neural network)
- Store partial trajectories over time
- Match by:
  - **Pitch contour** (not just static pitch)
  - **Harmonic interval relationships**
  - **Spectral evolution** (brightness changes over time)

**Add new search pass type**: `spass('spectral_layering', ...)`

---

## DETAILED APPROACH: Improving Pitch and Harmonic Analysis

### Problem Statement

AudioGuide's current pitch/harmonic analysis is insufficient for creating tonal, melodic, harmonic content. The core issues:

1. **Monophonic F0 only** - YIN algorithm gives single fundamental, no polyphonic capability
2. **No harmonic series extraction** - Doesn't identify individual partials and their amplitudes
3. **No temporal pitch tracking** - Uses median pitch per segment, loses contour information
4. **No melodic context** - Treats each segment independently, no interval/scale awareness
5. **Underutilized chroma features** - Pitch class descriptors available but not prominently used

### Technical Solution: Multi-Layered Pitch/Harmonic Analysis

#### Layer 1: Enhanced Fundamental Frequency (F0) Detection

**Current state**: `descriptordata.f0Seg()` (line 483)
- Simple median of non-zero YIN f0 estimates
- No amplitude or inharmonicity filtering
- Unreliable for noisy or complex sounds

**Improvement strategy**:

1. **Use the better built-in method**: `f0SegV2()` (lines 493-509)
   - Already exists but not used by default
   - Filters by amplitude threshold (absolute and relative)
   - Filters by inharmonicity
   - Takes median of top 3 most powerful frames
   - **Action**: Make this the default in `descriptordata.py`

2. **Add PYIN for polyphonic content**:
   ```python
   import librosa

   def f0_pyin(audio, sr, fmin=80, fmax=2000):
       """Probabilistic YIN - better for polyphonic/noisy signals"""
       f0, voiced_flag, voiced_probs = librosa.pyin(
           audio,
           fmin=fmin,
           fmax=fmax,
           sr=sr,
           frame_length=2048
       )
       # Return time-varying f0 with confidence weights
       return f0, voiced_probs
   ```

3. **Expand F0 range dynamically**:
   - Current: 200-1000 Hz (less than 3 octaves)
   - Better: 80-2000 Hz (4+ octaves)
   - Or auto-detect range based on spectral centroid

**Files to modify**:
- `audioguide/descriptordata.py:483-509` - Switch default to f0SegV2
- `audioguide/anallinkage.py:106-110` - Expand F0 range parameters
- `audioguide/defaults.py` - Add F0_METHOD option ('yin', 'pyin', 'auto')

#### Layer 2: Harmonic Series Extraction (Spectral Decomposition)

**Goal**: For each segment, extract fundamental + all harmonics with their amplitudes

**Method 1: FFT-based peak picking**
```python
def extract_harmonic_series_fft(audio, sr, f0, n_harmonics=16):
    """
    Extract harmonic partials using FFT

    Returns: [(freq1, amp1), (freq2, amp2), ...]
    """
    # Compute FFT
    fft = np.fft.rfft(audio)
    freqs = np.fft.rfftfreq(len(audio), 1/sr)
    magnitude = np.abs(fft)

    partials = []

    # For each expected harmonic
    for h in range(1, n_harmonics + 1):
        target_freq = f0 * h

        # Find spectral peak near target frequency (within ±50 cents)
        freq_tolerance = target_freq * 0.03  # ~50 cents
        mask = (freqs >= target_freq - freq_tolerance) & \
               (freqs <= target_freq + freq_tolerance)

        if np.any(mask):
            # Find peak in this region
            peak_idx = np.argmax(magnitude[mask])
            actual_freq = freqs[mask][peak_idx]
            actual_amp = magnitude[mask][peak_idx]

            partials.append((actual_freq, actual_amp))

    return partials
```

**Method 2: Sinusoidal modeling (using existing partialanalysis.py)**
```python
def extract_harmonic_series_sinusoidal(audio, sr, n_partials=16):
    """
    Use librosa STFT + peak tracking
    Improves on audioguide/partialanalysis.py
    """
    import librosa

    # STFT
    D = librosa.stft(audio, n_fft=4096, hop_length=512)
    magnitude = np.abs(D)

    # Track spectral peaks across time
    partials = []

    for frame_idx in range(magnitude.shape[1]):
        frame = magnitude[:, frame_idx]

        # Find peaks
        from scipy.signal import find_peaks
        peaks, properties = find_peaks(
            frame,
            height=np.max(frame) * 0.01,  # 1% of max
            distance=10  # Min distance between peaks
        )

        # Get frequencies and amplitudes
        freqs = librosa.fft_frequencies(sr=sr, n_fft=4096)[peaks]
        amps = properties['peak_heights']

        # Sort by amplitude, take top N
        top_indices = np.argsort(amps)[-n_partials:]

        frame_partials = list(zip(freqs[top_indices], amps[top_indices]))
        partials.append(frame_partials)

    return partials  # Time-varying partials
```

**Time-varying amplitude envelopes**:
```python
def extract_partial_envelopes(audio, sr, partials):
    """
    For each partial, extract amplitude envelope over time

    Returns: {freq: [amp_at_time1, amp_at_time2, ...]}
    """
    envelopes = {}

    for freq, amp in partials:
        # Bandpass filter around this frequency
        from scipy.signal import butter, filtfilt

        nyquist = sr / 2
        low = max(10, freq * 0.95) / nyquist
        high = min(nyquist - 10, freq * 1.05) / nyquist

        b, a = butter(4, [low, high], btype='band')
        filtered = filtfilt(b, a, audio)

        # Extract envelope using Hilbert transform
        from scipy.signal import hilbert
        analytic_signal = hilbert(filtered)
        envelope = np.abs(analytic_signal)

        # Downsample envelope (e.g., every 10ms)
        hop = int(sr * 0.01)  # 10ms
        envelope_downsampled = envelope[::hop]

        envelopes[freq] = envelope_downsampled

    return envelopes
```

**New descriptor**: `harmonic_series-seg`
- Array of (frequency, amplitude) tuples
- Stored in `sf_segment_descriptors`
- Used for spectral layering matching

**Files to create/modify**:
- `audioguide/spectralanalysis.py` - New module for harmonic extraction
- `audioguide/descriptordata.py` - Add `harmonic_series` descriptor type
- `audioguide/anallinkage.py` - Call harmonic extraction after IRCAM analysis

#### Layer 3: Pitch Contour and Melodic Descriptors

**Goal**: Capture pitch trajectory, not just static pitch

**New descriptors to add**:

1. **`pitch_contour`** - Array of f0 values over time
   ```python
   def compute_pitch_contour(audio, sr):
       f0, voiced = librosa.pyin(audio, fmin=80, fmax=2000, sr=sr)
       # Return only voiced frames
       return f0[voiced > 0.5]
   ```

2. **`pitch_slope`** - Rate of pitch change (cents/second)
   ```python
   def compute_pitch_slope(f0_array, hop_time):
       # Linear regression of log-frequency over time
       from scipy.stats import linregress
       time = np.arange(len(f0_array)) * hop_time
       log_f0 = np.log2(f0_array + 1e-8)  # Avoid log(0)
       slope, intercept, r_value, p_value, std_err = linregress(time, log_f0)

       # Convert to cents per second
       cents_per_second = slope * 1200  # 1 octave = 1200 cents
       return cents_per_second
   ```

3. **`pitch_stability`** - Variance of pitch (lower = more stable)
   ```python
   def compute_pitch_stability(f0_array):
       # Coefficient of variation in cents
       log_f0 = np.log2(f0_array + 1e-8)
       std_cents = np.std(log_f0) * 1200
       return std_cents
   ```

4. **`vibrato_rate` and `vibrato_depth`** - Periodic pitch modulation
   ```python
   def compute_vibrato(f0_array, hop_time):
       # Autocorrelation to find periodic modulation
       from scipy.signal import correlate

       # Detrend f0
       f0_detrended = f0_array - np.mean(f0_array)

       # Autocorrelation
       autocorr = correlate(f0_detrended, f0_detrended, mode='full')
       autocorr = autocorr[len(autocorr)//2:]

       # Find peaks (vibrato period)
       peaks, _ = find_peaks(autocorr, distance=int(0.1 / hop_time))  # Min 100ms period

       if len(peaks) > 0:
           vibrato_period = peaks[0] * hop_time
           vibrato_rate = 1 / vibrato_period  # Hz
           vibrato_depth = np.std(f0_detrended) * 1200  # cents
           return vibrato_rate, vibrato_depth

       return 0, 0
   ```

**Files to modify**:
- `audioguide/descriptordata.py` - Add melodic descriptors
- `audioguide/userclasses.py` - Expose in `SingleDescriptor (d)`

#### Layer 4: Harmonic Context and Interval Analysis

**Goal**: Understand melodic relationships between adjacent segments

**New descriptors**:

1. **`melodic_interval`** - Interval to previous segment (semitones)
   ```python
   def compute_melodic_interval(f0_current, f0_previous):
       if f0_previous == 0 or f0_current == 0:
           return 0
       semitones = 12 * np.log2(f0_current / f0_previous)
       return semitones
   ```

2. **`interval_class`** - Interval within one octave (0-11 semitones)
   ```python
   def interval_class(semitones):
       return int(semitones) % 12
   ```

3. **`pitch_class`** - Better utilization of existing chroma features
   ```python
   def compute_dominant_pitch_class(chroma_array):
       # chroma0-11 from IRCAM descriptors
       return np.argmax(chroma_array)  # 0=C, 1=C#, ..., 11=B
   ```

**Matching strategy**: Match by interval, not absolute pitch
```python
def match_by_melodic_interval(target_interval, corpus_segments):
    """
    Find corpus segment with similar melodic interval to previous
    Allows transposition while preserving melodic contour
    """
    best_match = None
    min_diff = float('inf')

    for seg in corpus_segments:
        corpus_interval = seg.melodic_interval
        diff = abs(target_interval - corpus_interval)

        if diff < min_diff:
            min_diff = diff
            best_match = seg

    return best_match
```

**Files to create/modify**:
- `audioguide/melodicmatching.py` - New module for interval/context matching
- `audioguide/simcalc.py` - Add `melodic_interval` search pass type

#### Layer 5: Chroma-Based Pitch Class Matching

**Current state**: `chroma0-11` descriptors exist but underutilized

**Improvement strategy**:

1. **Pitch class set matching**:
   ```python
   def chroma_similarity(target_chroma, corpus_chroma):
       """
       Cosine similarity between chroma vectors
       Invariant to transposition if rotated
       """
       from scipy.spatial.distance import cosine
       return 1 - cosine(target_chroma, corpus_chroma)

   def chroma_similarity_transposition_invariant(target_chroma, corpus_chroma):
       """
       Find best rotation (transposition) for maximum similarity
       """
       best_sim = 0
       for shift in range(12):
           rotated = np.roll(corpus_chroma, shift)
           sim = chroma_similarity(target_chroma, rotated)
           if sim > best_sim:
               best_sim = sim
       return best_sim
   ```

2. **Harmonic distance**:
   ```python
   def harmonic_distance(chroma1, chroma2):
       """
       Weight pitch classes by circle of fifths proximity
       """
       # Circle of fifths order: C, G, D, A, E, B, F#, C#, G#, D#, A#, F
       circle_of_fifths = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]

       # Create weighted difference
       weighted_diff = 0
       for i, pc in enumerate(circle_of_fifths):
           weight = 1.0 / (i + 1)  # Closer on circle = higher weight
           weighted_diff += abs(chroma1[pc] - chroma2[pc]) * weight

       return weighted_diff
   ```

3. **Add prominent chroma search pass**:
   ```python
   # In user options file:
   SEARCH = [
       spass('closest_percent', d('f0-seg', norm=1), percent=10),
       spass('closest', d('chromas')),  # Package of all 12 chroma features
       spass('closest', d('mfccs'))
   ]
   ```

**Files to modify**:
- `audioguide/simcalc.py` - Add chroma-specific distance metrics
- `audioguide/userclasses.py` - Create `chromas` descriptor package

#### Layer 6: Harmonic Template Matching

**Goal**: Match entire spectral fingerprint, not individual descriptors

**Concept**: Treat harmonic series as a template/pattern

```python
def harmonic_template_distance(target_partials, corpus_partials):
    """
    Compare two harmonic series by:
    1. Frequency ratios (harmonic structure)
    2. Amplitude distribution (spectral envelope)
    """

    # Normalize to fundamental = 1.0
    target_ratios = [f / target_partials[0][0] for f, a in target_partials]
    corpus_ratios = [f / corpus_partials[0][0] for f, a in corpus_partials]

    # Extract amplitude envelopes
    target_amps = np.array([a for f, a in target_partials])
    corpus_amps = np.array([a for f, a in corpus_partials])

    # Normalize amplitudes
    target_amps /= np.sum(target_amps)
    corpus_amps /= np.sum(corpus_amps)

    # Compare frequency ratios (harmonic structure)
    freq_distance = 0
    for t_ratio in target_ratios[:8]:  # Compare first 8 harmonics
        # Find closest corpus ratio
        closest = min(corpus_ratios, key=lambda x: abs(x - t_ratio))
        freq_distance += abs(t_ratio - closest)

    # Compare amplitude distribution (spectral envelope)
    amp_distance = np.sum(np.abs(target_amps - corpus_amps))

    # Weighted combination
    return 0.5 * freq_distance + 0.5 * amp_distance
```

**New search pass type**: `spass('harmonic_template', ...)`

**Files to create**:
- `audioguide/harmonicmatching.py` - Template matching algorithms

### Integration Strategy

**Descriptor priority for pitched content**:

```python
# Traditional AudioGuide (good for timbre, bad for pitch)
SEARCH_TIMBRE = [
    spass('closest_percent', d('effDur-seg', norm=1), percent=25),
    spass('closest', d('mfccs'))
]

# Improved for pitched content (new approach)
SEARCH_PITCHED = [
    spass('closest_percent', d('f0-seg', norm=1), percent=10),      # Narrow by pitch
    spass('closest', d('harmonic_series-seg')),                     # Match harmonic structure
    spass('closest', d('chromas')),                                 # Pitch class similarity
    spass('closest', d('harmoniccentroid', 'spectralcentroid'))     # Brightness
]

# Melodic context matching (new approach)
SEARCH_MELODIC = [
    spass('melodic_interval', tolerance_cents=50),                  # Match interval contour
    spass('closest', d('pitch_stability')),                         # Match vibrato/stable notes
    spass('closest', d('chromas')),                                 # Pitch class
]
```

**Backward compatibility**: All new features opt-in
- Default behavior unchanged (uses IRCAM + existing descriptors)
- New descriptors available via options: `USE_HARMONIC_ANALYSIS = True`

### Performance Considerations

1. **Harmonic extraction is expensive**:
   - FFT on every segment
   - Peak tracking across time
   - **Solution**: Cache results, parallel processing

2. **Increased memory usage**:
   - Storing time-varying partials
   - **Solution**: Configurable max partials (default 8-16)

3. **Slower matching**:
   - More complex distance calculations
   - **Solution**: Pre-filter by f0, then use expensive harmonic matching

### Summary of Technical Improvements

| Current | Improved |
|---------|----------|
| Median f0 per segment | PYIN with confidence + pitch contour tracking |
| No harmonic extraction | FFT + sinusoidal modeling for partials + amplitudes |
| Single-value descriptors | Time-varying amplitude envelopes per partial |
| No melodic context | Interval analysis, pitch class matching |
| Chroma underutilized | Chroma similarity, transposition-invariant matching |
| Timbre-focused search | Pitch-focused, harmonic template, melodic contour |

**Files to create**:
- `audioguide/spectralanalysis.py` - Harmonic series extraction
- `audioguide/melodicmatching.py` - Interval and contour matching
- `audioguide/harmonicmatching.py` - Harmonic template algorithms

**Files to modify**:
- `audioguide/descriptordata.py` - Add new descriptor types
- `audioguide/anallinkage.py` - Integrate new analysis
- `audioguide/simcalc.py` - Add new distance metrics
- `audioguide/defaults.py` - Add configuration options

---

#### 5. Enhanced .RPP Export with Clip Gain Automation

**File to rewrite**: `audioguide/fileoutput/reaper.py`

**CRITICAL DISCOVERY: Use TAKEENV, not VOLUMEENV!**

Research reveals that item-level volume automation (clip gain) uses **`<TAKEENV>`**, not `<VOLUMEENV>`:
- **VOLUMEENV** = Track-level volume automation (post-FX)
- **VOLENV** = Track-level trim volume (offset to VOLUMEENV)
- **TAKEENV** = Item/take-level volume (pre-FX) - **THIS IS WHAT WE NEED!**

**Correct RPP structure for clip gain automation**:

```
<ITEM
  POSITION  4.0
  LENGTH    2.0
  NAME      "corpus_sound.wav"
  VOLPAN    1.0 0.0 1.0 -1.0
  <TAKE
    NAME    "corpus_sound.wav"
    <SOURCE WAVE
      FILE  "/path/to/corpus_sound.wav"
    >
    <TAKEENV
      NAME "Volume"
      ACT 1
      VIS 1
      LANEHEIGHT 0 0
      ARM 0
      DEFSHAPE 0 -1 -1
      <PT 4.0 1.0 0>
      <PT 4.5 0.707 0>
      <PT 5.0 1.0 0>
      <PT 5.5 0.5 0>
      <PT 6.0 1.0 0>
    >
  >
>
```

**Key nested structure**: `ITEM > TAKE > TAKEENV > PT` (points)

**TAKEENV parameters**:
- `NAME "Volume"` - Identifies this as a volume envelope
- `ACT 1` - Envelope is active
- `VIS 1` - Envelope is visible
- `ARM 0` - Envelope is not armed for automation
- `DEFSHAPE 0 -1 -1` - Default shape for new points
- `<PT position value shape>` - Automation points:
  - `position`: Absolute time in project (seconds)
  - `value`: Volume level (1.0 = 0dB, 0.707 ≈ -3dB, 0.5 = -6dB, etc.)
  - `shape`: Curve type (0 = linear, 1-5 = various curves)

**Implementation requirements**:

1. **Modify AudioGuide's current structure**:
   - Currently creates `<ITEM>` with `<SOURCE WAVE>` directly
   - Must wrap `<SOURCE>` inside `<TAKE>` chunk
   - Add `<TAKEENV>` as sibling to `<SOURCE>` within `<TAKE>`

2. **Time-varying clip gain**:
   - Generate automation points from `clip_gain_envelope` array
   - Convert amplitude values to linear scale (0.0 to 1.0+)
   - Sample at appropriate rate (e.g., every 10ms or at spectral evolution keyframes)
   - Write as `<PT>` tags inside `<TAKEENV>`

3. **USER PREFERENCE: No transposition by default, varispeeding if needed**:
   - **Default**: No transposition - only position and gain changes to corpus sounds
   - **If transposition selected**: Use varispeeding (playback rate), NOT algorithmic pitch shifting
   - **Implication for spectral layering**:
     - **Cannot use transposition** for matching partials (would cause desync)
     - **Must find corpus sounds with natural frequencies** matching target partials
     - More restrictive matching, but preserves audio quality
     - Corpus needs to contain sounds across wide frequency range
   - **Implementation**:
     - Default: No PLAYRATE tag (plays at original pitch)
     - If user enables transposition: `RPP_TRANS_AFFECTS_SPEED = True` (varispeeding)

4. **Track-level volume automation** (optional):
   - Add `<VOLUMEENV>` at track level if global amplitude changes needed
   - Separate concern from item-level clip gain

4. **Improved track organization**:
   - One track per spectral layer (e.g., "Fundamental", "Harmonic 2", "Harmonic 3", etc.)
   - Or organize by frequency range

**New data structure**:
```python
{
    'file': filepath,
    'time': timeInScore,
    'duration': duration,
    'skip': sfSkip,
    'transposition': semitones,
    'amp': amplitude,  # Base amplitude
    'clip_gain_envelope': [(time1, gain1), (time2, gain2), ...],  # NEW
    'fadein': envAttackSec,
    'fadeout': envDecaySec
}
```

**Function to add**: `write_clip_gain_automation()`

#### 6. Melodic/Harmonic Context Matching

**File to create**: `audioguide/melodicmatching.py`

**Add melodic descriptors**:
- **Pitch contour** (rising, falling, stable)
- **Interval sequence** (melodic intervals between segments)
- **Scale degree** (requires key detection)
- **Harmonic function** (tonic, dominant, subdominant - if chords detected)

**Add matching strategies**:
- Match by **melodic interval** (not absolute pitch)
- Match by **pitch class** (using chroma features)
- Match by **harmonic progression** (if analyzing chords)

#### 7. Improved Descriptor Weights for Pitched Content

**File to modify**: `audioguide/defaults.py`, examples

**Add default search strategies for pitched content**:
```python
SEARCH_PITCHED = [
    spass('closest_percent', d('f0-seg', norm=1), percent=10),  # Narrow by pitch first
    spass('closest', d('chroma0-11')),                          # Then by pitch class
    spass('closest', d('harmoniccentroid', 'spectralcentroid')) # Then by brightness
]
```

---

## Implementation Roadmap

### Phase 1: Enhanced Spectral Analysis
1. Improve `partialanalysis.py` - make it robust and documented
2. Add harmonic series extraction to `descriptordata.py`
3. Store spectral fingerprints per segment
4. Add melodic contour descriptors

### Phase 2: Spectral Layering Algorithm
1. Create `spectrallayering.py` module
2. Implement `spectral_layering_match()` function
3. Add new search pass type `'spectral_layering'`
4. Integrate into main concatenation flow in `__init__.py`

### Phase 3: Clip Gain Automation
1. Modify event data structure to include `clip_gain_envelope`
2. Compute gain envelopes in spectral layering algorithm
3. Rewrite `fileoutput/reaper.py` to support `<VOLUMEENV>`
4. Add track organization by spectral layer

### Phase 4: Melodic Matching Improvements
1. Create `melodicmatching.py` module
2. Add pitch contour descriptors
3. Add interval-based matching
4. Integrate chroma features prominently

### Phase 5: Testing & Examples
1. Create example script: `examples/14-spectralLayering.py`
2. Test with harmonic material (orchestral, vocal, tonal synth)
3. Compare timbral vs. spectral layering approaches
4. Document in HTML docs

---

## Key Files to Modify/Create

### Modify
- `audioguide/__init__.py` - Add spectral layering execution path
- `audioguide/concatenativeclasses.py` - Add spectral layering event generation
- `audioguide/partialanalysis.py` - Elevate from experimental to production
- `audioguide/descriptordata.py` - Add harmonic series extraction
- `audioguide/anallinkage.py` - Add melodic contour descriptors
- `audioguide/simcalc.py` - Add spectral layering search pass
- `audioguide/fileoutput/reaper.py` - **REWRITE** with clip gain automation
- `audioguide/defaults.py` - Add options for spectral layering mode
- `audioguide/userclasses.py` - Add API for spectral layering config

### Create
- `audioguide/spectrallayering.py` - Core spectral reconstruction algorithm
- `audioguide/melodicmatching.py` - Melodic/harmonic matching utilities
- `examples/14-spectralLayering.py` - Example usage
- `examples/15-melodicMatching.py` - Example for pitched content

---

## Configuration Example (Future)

```python
from audioguide import *

TARGET = tsf('piano_melody.aiff', thresh=-30)

CORPUS = [
    csf('synth_corpus/*.aiff', limit='f0-seg > 100 and f0-seg < 2000')
]

# NEW: Spectral layering mode
CONCATENATE_MODE = 'spectral_layering'  # vs. 'timbre_matching' (default)

SEARCH = [
    spass('spectral_layering',
          target_descriptor=d('harmonic_series'),  # NEW descriptor
          max_partials=8,                          # Layer up to 8 partials
          pitch_tolerance_cents=50)
]

SUPERIMPOSE = si(
    maxSegment=8,                    # More layers needed for partials
    ampThreshold=-60                 # Allow quieter layers
)

# IMPROVED: .rpp with clip gain automation
RPP_FILEPATH = 'output/spectral_layered.rpp'
RPP_INCLUDE_TARGET = True
RPP_CLIP_GAIN_AUTOMATION = True      # NEW: Enable TAKEENV automation
RPP_TRACK_BY_PARTIAL = True          # NEW: One track per harmonic
RPP_TRANS_AFFECTS_SPEED = True       # Use varispeeding IF transposition enabled
                                     # But spectral layering won't transpose!
RPP_AUTOLAUNCH = True

# OPTIONAL: FluCoMa segmentation
SEGMENTATION_METHOD = 'novelty'      # 'power' (default) or 'novelty' (FluCoMa)
NOVELTY_THRESHOLD = 0.5              # Higher = fewer segments (whole-file feel)
```

---

## Expected Outcomes

1. **Better harmonic content**:
   - Corpus sounds selected to match specific partials in target
   - Layered to recreate full harmonic spectrum

2. **Improved melodic matching**:
   - Pitch contour awareness
   - Interval-based selection
   - Chroma/pitch class matching

3. **Professional .rpp files**:
   - Clip gain automation for dynamic amplitude changes
   - Organized tracks by spectral layer
   - Ready for mixing in Reaper

4. **Flexible synthesis modes**:
   - `'timbre_matching'` (current approach) for noisy/percussive material
   - `'spectral_layering'` (new approach) for pitched/harmonic material

---

## Validation Test Case: Cello from Sine Tones

### The Perfect Test

**Objective**: Reconstruct a cello melody using only a corpus of pure sine tones

**Why this is ideal**:
- **Cello target** provides:
  - Clear fundamental frequency (melody)
  - Rich harmonic series (partials at f0, 2f0, 3f0, 4f0...)
  - Vibrato (pitch modulation)
  - Temporal envelope changes (bow attacks, sustains, releases)
  - Spectral evolution over time (brightness changes)

- **Sine tone corpus** provides:
  - Pure frequencies (single partials, no harmonics)
  - Simple, predictable spectral content
  - Perfect building blocks for additive synthesis
  - No transposition needed (generate/use sines at all needed frequencies)

**What this validates**:
1. ✅ **Harmonic series extraction** - Can we extract cello's partials?
2. ✅ **F0 tracking** - Can we follow the melody accurately?
3. ✅ **Pitch contour matching** - Can we handle vibrato and glides?
4. ✅ **Spectral layering algorithm** - Can we select the right sines for each partial?
5. ✅ **Amplitude matching** - Can we weight each sine correctly?
6. ✅ **TAKEENV automation** - Can we recreate cello's temporal envelope?
7. ✅ **No transposition** - Sines at exact frequencies (no varispeeding)
8. ✅ **RPP export** - Does the Reaper project render correctly?

### Expected Result

**For each cello note**:
```
Cello note: A3 (220 Hz) with vibrato
  └─ Extract harmonics:
      ├─ Fundamental (220 Hz, -6 dB)    → Sine at 220 Hz + TAKEENV
      ├─ Harmonic 2 (440 Hz, -12 dB)   → Sine at 440 Hz + TAKEENV
      ├─ Harmonic 3 (660 Hz, -18 dB)   → Sine at 660 Hz + TAKEENV
      ├─ Harmonic 4 (880 Hz, -20 dB)   → Sine at 880 Hz + TAKEENV
      ├─ Harmonic 5 (1100 Hz, -24 dB)  → Sine at 1100 Hz + TAKEENV
      └─ Harmonic 6 (1320 Hz, -28 dB)  → Sine at 1320 Hz + TAKEENV

Each sine has time-varying gain automation matching cello's amplitude envelope.
```

**Success metrics**:
- ✅ Recognizable melody (pitch accuracy)
- ✅ Timbral resemblance to cello (harmonic balance)
- ✅ Dynamic expression (amplitude envelopes via TAKEENV)
- ✅ Smooth rendering in Reaper (no glitches, correct sync)

### Corpus Preparation

**Option 1: Pre-generated sine bank**
```python
import numpy as np
import soundfile as sf

# Generate sine tones from 65 Hz to 2000 Hz (every 10 Hz)
for freq in range(65, 2001, 10):
    duration = 5.0  # 5 seconds each
    sr = 48000
    t = np.linspace(0, duration, int(sr * duration))
    sine = np.sin(2 * np.pi * freq * t)

    # Apply fade in/out to avoid clicks
    fade_samples = int(sr * 0.01)  # 10ms fade
    sine[:fade_samples] *= np.linspace(0, 1, fade_samples)
    sine[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    filename = f'sine_{freq:04d}Hz.wav'
    sf.write(f'corpus/sines/{filename}', sine, sr)

# Result: ~200 sine tone files covering full frequency range
```

**Option 2: On-demand generation**
- Analyze target first to find needed frequencies
- Generate only required sines
- Smaller corpus, faster analysis

### Implementation Steps

1. **Prepare corpus**: Generate sine tone bank (65-2000 Hz, 10 Hz intervals)
2. **Analyze cello target**: Extract harmonic series for each segment
3. **Configure AudioGuide**:
   ```python
   TARGET = tsf('cello_melody.wav', thresh=-40)
   CORPUS = [csf('corpus/sines/*.wav')]
   CONCATENATE_MODE = 'spectral_layering'
   SEARCH = [
       spass('closest', d('f0-seg', norm=1), tolerance_cents=50)
   ]
   SUPERIMPOSE = si(maxSegment=16)  # Up to 16 harmonics layered
   RPP_FILEPATH = 'output/cello_from_sines.rpp'
   RPP_CLIP_GAIN_AUTOMATION = True
   RPP_TRACK_BY_PARTIAL = True
   ```
4. **Run concatenation**: AudioGuide matches sines to cello partials
5. **Open in Reaper**: Verify TAKEENV automation, track organization
6. **Render and compare**: Does it sound like additive synthesis of cello?

### What We Learn

**If successful**:
- Spectral reconstruction works!
- TAKEENV automation is correctly implemented
- Harmonic analysis is accurate
- Ready to try with more complex targets/corpora

**If issues arise**:
- Missing partials → Need better harmonic extraction
- Wrong amplitudes → Need better amplitude matching
- Timing issues → Check TAKEENV time alignment
- Noisy result → Need more harmonics or better envelope smoothing

**This is essentially additive synthesis via concatenative synthesis** - the ultimate test of the spectral layering approach!

---

## Technical Challenges

1. **Computational cost**:
   - Spectral layering requires analyzing many more corpus sounds per segment
   - May need optimization or parallel processing

2. **Phase cancellation**:
   - Layering corpus sounds may cause phase issues
   - May need phase-aware selection or randomization

3. **Transposition quality**:
   - Matching partials requires precise pitch shifting
   - Current Reaper playback speed method may degrade quality
   - May need `RPP_TRANS_AFFECTS_SPEED = False` with pitch shift plugin

4. **Harmonic richness of corpus**:
   - Corpus sounds need strong fundamentals to match target partials
   - May need corpus filtering/recommendation system

5. **Reaper .rpp format limitations**:
   - Need to ensure `<VOLUMEENV>` is correctly formatted
   - May need to test with various Reaper versions
   - Documentation on .rpp format is informal (reverse-engineered)

---

## Notes for Claude

- When implementing improvements, **start with Phase 3** (clip gain automation in .rpp) as it's the most critical user-requested feature
- **Read existing code carefully** before modifying - AudioGuide is mature and well-structured
- **Maintain backward compatibility** - add new modes rather than replacing existing functionality
- **Test incrementally** - each phase should produce working output
- **Preserve the existing defaults** - spectral layering should be opt-in
- The user has already had Grok explore the codebase, so context is warmed up
- **DO NOT implement yet** - this document is for future reference only

---

## Python Libraries for RPP Generation

### Research Findings: reathon vs. reapy

**Gemini research summary**:

1. **reapy**:
   - Excellent automation support (VOLENV, TAKEENV)
   - Wrapper for REAPER ReaScript API
   - **Requires running REAPER instance** (dealbreaker for offline generation)
   - Best for interactive scripting, not batch file generation

2. **reathon**:
   - Designed for programmatically constructing RPP files from scratch
   - Does NOT have explicit TAKEENV/envelope support
   - BUT: Has `.props` system for arbitrary property manipulation
   - Can potentially be extended to support TAKEENV

3. **rpp** library:
   - Low-level parser/emitter
   - No high-level abstractions
   - Would require manual envelope implementation

### Should We Use reathon?

**Verdict: Maybe, but not essential**

**Pros**:
- Cleaner API than string formatting
- Could simplify track/item/take hierarchy
- Extensible via `.props` for custom chunks

**Cons**:
- Doesn't support TAKEENV out of the box
- Would still need to manually construct envelope chunks
- AudioGuide's current `reaper.py` is only 47 lines - not complex
- Adding dependency may not be worth it

**Recommendation**:
- **For initial implementation**: Stick with AudioGuide's current string-based approach
- **Extend it** to support TAKE wrapping and TAKEENV chunks
- **Later optimization**: Could refactor to use reathon if complexity grows

**Key insight**: Whether using reathon or raw strings, we need to understand the TAKE > TAKEENV > PT structure (which we now do from Gemini research).

---

## Assessment of Alternative Improvement Plans

### CLAUDE_PLAN.md (FluCoMa Integration) - Not Recommended

A previous AI assistant created a plan to integrate FluCoMa (Fluid Corpus Manipulation) tools. **This plan should be ignored** for the following reasons:

**What the FluCoMa plan suggests**:
1. Replace IRCAM descriptors with FluCoMa descriptors
2. Use FluCoMa's OnsetSlice/NoveltySlice for segmentation
3. Use "fluid-learn~" for machine learning timbre synthesis
4. Requires building external FluCoMa binaries

**Why this muddies context**:
1. **Wrong focus**: Improves what AudioGuide already does well (timbre matching) instead of addressing the actual problems (pitched/harmonic content)
2. **Architectural mismatch**:
   - IRCAM descriptors are already excellent (perceptually weighted, harmonically aware)
   - FluCoMa descriptors heavily overlap with IRCAM (MFCCs, spectral shape, etc.)
   - Replacing vs. augmenting is unnecessary complexity
3. **Realtime-focused**: FluCoMa excels at realtime corpus exploration; user wants offline processing
4. **External dependency**: Requires building C++ binaries; AudioGuide already has IRCAM binary included
5. **Missing user goals**: No mention of:
   - Spectral reconstruction approach
   - Harmonic layering strategy
   - Clip gain automation in .rpp
   - Pitch/melody/harmony improvements

**What to use instead**:
- AudioGuide's existing infrastructure (IRCAM descriptors, partial analysis)
- Python libraries already available (librosa, scipy, numpy)
- Focus on spectral decomposition + harmonic layering (detailed in this document)

**Verdict**: The FluCoMa plan is well-intentioned but fundamentally misaligned with user goals. It optimizes the wrong thing and adds unnecessary complexity.

---

## Questions to Resolve Before Implementation

1. What sample rate/FFT size for harmonic series extraction?
2. How many partials to extract per segment (default 8? 16?)?
3. Should spectral layering be a new CONCATENATE_MODE or a new search pass type?
4. Should we use time-varying descriptors for pitch contour or new descriptor type?
5. How to handle inharmonic sounds (e.g., bells, gongs) in spectral layering?
6. ~~Should corpus sounds be transposed via speed change or pitch shift plugin in Reaper?~~ **ANSWERED**: Must use pitch shifting (RPP_TRANS_AFFECTS_SPEED=False) to preserve duration and keep spectral layers synchronized.
7. What automation point sampling rate for clip gain (10ms? 20ms? Or match spectral analysis hop size?)?

---

## References

- AudioGuide documentation: `/Applications/AudioGuide/audioguide/docs_v1.79.html`
- Reaper RPP format: Reverse-engineered, see `fileoutput/reaper.py`
- Partial analysis: `audioguide/partialanalysis.py` (experimental)
- Example configurations: `/Applications/AudioGuide/audioguide/examples/`

---

## Key Research Discoveries (2025-11-06)

### Critical .RPP Finding: TAKEENV vs. VOLUMEENV

**Problem**: Initial plan incorrectly assumed `<VOLUMEENV>` for clip gain automation.

**Solution**: Use `<TAKEENV>` instead:
- **VOLUMEENV**: Track-level volume automation (post-FX) - NOT what we need
- **TAKEENV**: Item/take-level volume automation (pre-FX) - **THIS IS CLIP GAIN!**

**Correct structure**:
```
ITEM > TAKE > TAKEENV > PT (automation points)
```

**Implementation impact**:
- Must wrap `<SOURCE>` inside `<TAKE>` chunk (AudioGuide currently doesn't)
- Add `<TAKEENV>` as sibling to `<SOURCE>` within `<TAKE>`
- Each `<PT>` point: `<PT absolute_time linear_value shape>`

### Critical Design Decision: No Transposition for Spectral Layering

**User preference clarified**:
- Default: **No transposition** - only position and gain changes
- If transposition needed: Use **varispeeding** (playback rate), NOT algorithmic pitch shifting
- User wants to preserve audio quality, no stretching algorithms

**Implication for spectral layering approach**:
Since transposition causes desync with varispeeding, spectral layering must work **without transposition**:

**Revised strategy**:
1. **Extract target harmonics**: Fundamental at 220Hz, H2 at 440Hz, H3 at 660Hz, etc.
2. **Match corpus by natural frequency**:
   - Find corpus sound with f0 ≈ 220Hz for fundamental
   - Find corpus sound with f0 ≈ 440Hz for H2
   - Find corpus sound with f0 ≈ 660Hz for H3
   - No transposition needed!
3. **Adjust only gain** (via TAKEENV) to match target partial amplitudes
4. **Tolerance**: Allow ±50 cents matching tolerance

**Corpus requirements**:
- Need sounds across wide frequency range (80 Hz - 2000 Hz)
- Variety of fundamentals to match different target partials
- Example: Corpus with f0 values at 100, 150, 220, 330, 440, 660, 880, 1320 Hz etc.

**Advantages**:
- No audio degradation from pitch shifting
- Clean, natural sound quality
- Simpler implementation (no PLAYRATE tag needed)

**Trade-offs**:
- More restrictive matching (corpus must contain right frequencies)
- May need larger, more diverse corpus
- Some target partials may not find good matches

### Python Library Assessment

**Libraries evaluated**:
1. **reapy**: Requires running REAPER - not suitable for offline batch generation
2. **reathon**: No built-in TAKEENV support, but extensible - possibly useful later
3. **rpp**: Too low-level

**Decision**: Extend AudioGuide's existing `reaper.py` (47 lines) with TAKE/TAKEENV support. Don't add external dependencies yet.

### Segmentation Improvements: FluCoMa Slicing Tools

**User question**: Would FluCoMa's novelty slice / pitch slice help for "whole-file feel"?

**Current AudioGuide segmentation**: Power-based onset detection (`segmentationAlgoV2` in `sfsegment.py:29`)
- Simple, functional
- May miss musically meaningful boundaries
- No pitch-aware segmentation

**FluCoMa slicing tools** (CLI available):
1. **FluidNoveltySlice**: Detects changes in spectral content
   - Better for timbral transitions
   - Could preserve "whole-file feel" by detecting fewer, more meaningful boundaries
   - Good for slowly-evolving sounds

2. **FluidOnsetSlice**: Similar to AudioGuide's onset detection but more sophisticated

3. **FluidAmpSlice**: Amplitude-based (similar to current approach)

4. **FluidTransientSlice**: Detects transients vs. sustained sounds

**Verdict**: **Yes, potentially useful!**
- FluCoMa slicing as **optional alternative** to current segmentation
- User can choose: `SEGMENTATION_METHOD = 'power'` (default) or `'novelty'` (FluCoMa)
- For whole-file feel: `FluidNoveltySlice` with high threshold = fewer segments
- Would require FluCoMa CLI tools installed (external dependency)

**Implementation approach**:
- Keep AudioGuide's default segmentation
- Add optional FluCoMa wrapper (`flucoma_segmentation.py`)
- User opts in via configuration
- Falls back to default if FluCoMa not installed

**Re-evaluation of FluCoMa**:
- Previously rejected for **descriptor replacement** (bad idea)
- But **segmentation tools** could be useful (good idea!)
- Focused, limited integration vs. wholesale replacement

### F0 Analysis: Current Best Practices

**User question**: Is YIN/PYIN the best pitch analysis tool now?

**Current state-of-the-art** (2025):

1. **PYIN (Probabilistic YIN)** - librosa implementation
   - Good for noisy/polyphonic signals
   - Provides confidence scores
   - Better than basic YIN
   - ✅ **Good choice for AudioGuide**

2. **CREPE** (CNN-based) - Deep learning pitch tracker
   - State-of-the-art accuracy
   - Better with complex/polyphonic material
   - Requires tensorflow (heavy dependency)
   - Slower than PYIN
   - ⚠️ **Overkill for AudioGuide's needs**

3. **YIN** (current AudioGuide)
   - Classic, reliable
   - Fast
   - Struggles with noisy/polyphonic sounds
   - ❌ **Should upgrade to PYIN**

4. **SPICE** (Google's model)
   - Neural network-based
   - Very accurate
   - Heavy dependency
   - ⚠️ **Overkill**

**Recommendation for AudioGuide**:
- **Upgrade to PYIN** (librosa.pyin)
- Light dependency (librosa already suggested for harmonic analysis)
- Significant improvement over YIN
- Good balance of accuracy/speed
- No need for heavy ML models (CREPE/SPICE)

**Fallback chain**:
```python
# Preferred
try:
    f0, confidence = librosa.pyin(audio, fmin=80, fmax=2000)
except:
    # Fallback to IRCAM's YIN
    f0 = ircam_yin(audio)
```

### Tool Evaluation Summary

**Rejected**:
- FluCoMa for descriptor replacement: Wrong focus
- reapy: Requires running REAPER instance
- CREPE/SPICE: Overkill, heavy dependencies

**Reconsidered - Potentially Useful**:
- **FluCoMa slicing tools**: Optional segmentation improvement for whole-file feel
  - Requires CLI tools installed
  - Opt-in feature, not required

**Recommended**:
- **PYIN** (librosa): Upgrade from YIN for better pitch tracking
- reathon: Clean API patterns for RPP generation (may use later)
- ReaTeam State Chunk Definitions: Essential reference for .rpp format

---

**Last Updated**: 2025-11-06 (with pitch/harmonic analysis + RPP research + user clarifications)
**Claude Agent**: sonnet-4-5-20250929

---

## User Preference Clarifications (2025-11-06)

1. **No transposition by default**: Only position and gain changes to audio
2. **If transposition needed**: Use varispeeding (playback rate), NOT algorithmic pitch shifting
3. **Implication**: Spectral layering must match corpus sounds by natural frequency (no transposition)
4. **Segmentation**: Interested in FluCoMa's novelty/pitch slice for whole-file feel
5. **F0 analysis**: Upgrade to PYIN recommended (better than current YIN)

---

## Starting a New Implementation Session

**For fresh Claude context, begin with**:

1. **Read the Executive Summary** (top of this file) - 5 minutes to get oriented

2. **Confirm current status**:
   - Has Grok completed proof-of-concept test? (Check `test_output/RECONSTRUCTION_TEST_REPORT.md`)
   - Are sine corpus files generated? (Check `test_corpus/sines/`)
   - Does test .rpp file work in Reaper?

3. **Choose your implementation phase**:

   **Phase 1 - RPP Export Enhancement** (Highest priority, most immediate value)
   - File to modify: `audioguide/fileoutput/reaper.py`
   - Add TAKE wrapping and TAKEENV support
   - Test with existing AudioGuide output
   - Reference: "Enhanced .RPP Export" section in this doc

   **Phase 2 - Harmonic Analysis**
   - Files to create: `audioguide/spectralanalysis.py`
   - Implement harmonic series extraction (FFT + peak picking)
   - Add PYIN f0 tracking
   - Reference: "Layer 1-2" in pitch/harmonic improvements section

   **Phase 3 - Spectral Layering Algorithm**
   - File to create: `audioguide/spectrallayering.py`
   - Match corpus to target partials by natural frequency
   - Compute gain envelopes per partial
   - Reference: "Spectral Layering Algorithm" section

   **Phase 4 - Melodic Improvements**
   - Add pitch contour, interval, chroma descriptors
   - Reference: "Layer 3-6" in pitch/harmonic improvements section

4. **Before coding, ask user**:
   - Which phase should we start with?
   - What's the test target/corpus to use?
   - Any specific constraints or priorities?

5. **Key files to read first**:
   ```
   audioguide/fileoutput/reaper.py          # Current RPP export (47 lines)
   audioguide/concatenativeclasses.py       # Core concatenation logic
   audioguide/descriptordata.py             # Descriptor management
   audioguide/partialanalysis.py            # Experimental partial tracking
   ```

6. **Testing approach**:
   - Start simple: Modify RPP export to add one TAKEENV with static points
   - Validate: Open in Reaper, check automation visible
   - Iterate: Add time-varying points, multiple takes, etc.
   - Test case: Use cello-from-sines when ready

7. **Don't forget**:
   - Maintain backward compatibility (new features opt-in)
   - Document new options in `defaults.py`
   - Add example configuration file
   - Test with existing AudioGuide examples first

**Quick sanity checks**:
- ✅ Do you understand what spectral reconstruction synthesis is?
- ✅ Do you know the difference between TAKEENV and VOLUMEENV?
- ✅ Do you understand why we can't use transposition for spectral layering?
- ✅ Have you read the Executive Summary?

**If yes to all → you're ready to start coding!**

**If no → re-read relevant sections in this document first.**

---

## Session History

### 2025-11-06 - Planning & Research Session
- Explored AudioGuide codebase (3 parallel agents)
- Researched RPP format (Gemini - discovered TAKEENV vs VOLUMEENV)
- Evaluated Python libraries (reathon, reapy)
- Assessed FluCoMa (rejected for descriptors, accepted for segmentation)
- Clarified user preferences (no transposition, varispeeding only)
- Designed 6-layer pitch/harmonic improvement strategy
- Created cello-from-sines test case
- Generated Grok prompt for proof-of-concept
- **Deliverables**: CLAUDE_INIT.md (this file), GROK_PROMPT_CELLO_TEST.md

### Next Session - Implementation
- Status: Awaiting proof-of-concept results
- Focus: TBD based on user priority (likely RPP export first)

### 2025-11-10 - Implementation Session

**Status**: Built spectral modules + validated baseline AudioGuide pipeline

#### What We Built

1. **audioguide-claude/** - Fork of AudioGuide v1.79 with enhancements:
   - **spectralanalysis.py** - FFT-based harmonic extraction
     - `extract_harmonic_series_fft()` - Finds f0 + harmonics with amplitudes
     - `extract_partial_envelopes()` - Time-varying amplitude tracking per partial
     - `f0_pyin()` - Improved pitch detection (librosa PYIN + fallback)
   - **spectrallayering.py** - Corpus matching by natural frequency
     - `spectral_layering_match()` - Matches corpus to target harmonics (NO transposition)
     - `compute_gain_envelope()` - Time-varying gain adjustments
     - `freq_to_cents()` - Frequency matching within tolerance
   - **reaper.py (enhanced)** - TAKEENV clip gain automation
     - `format_takeenv()` - Creates TAKEENV chunk with PT automation points
     - `db_to_linear()` - Converts dB to linear for Reaper
     - TAKEENV structure: ITEM > SOURCE > TAKEENV > PT points (not TAKE wrapper - caused issues)
   - **userinterface.py (fixed)** - Python 3.13 compatibility
     - Fixed bytes/string handling in `_render_sub()`

2. **Test Scripts Created**:
   - **test_cello_spectral_reconstruction.py** - Custom end-to-end test
     - Created SimpleAnalInterface (minimal IRCAM replacement)
     - Analyzed cello: Found F0 726 Hz, 16 harmonics
     - Matched 6 upper partials (H2-H7) to sine corpus
     - Generated RPP + WAV outputs
   - **examples/cello_sines_baseline.py** - Standard AudioGuide config
     - Uses existing AudioGuide pipeline
     - Matches sine corpus to cello by f0 + duration/power
     - Allows 8-layer superimposition

#### Test Results

**Custom Test (test_cello_spectral_reconstruction.py)**:
- ❌ RPP had parsing errors (PT format issues, envelope timing bugs)
- ✅ WAV rendered (2.4MB) but only captured upper harmonics (1.4-5.0 kHz)
- **Issue**: Missing fundamental (728 Hz) - sine corpus may not have exact match
- **Lesson**: Need to validate foundation before adding complexity

**Baseline Test (cello_sines_baseline.py)** - ✅ SUCCESS:
- ✅ Analyzed 128 sine files + 26.7 sec cello target
- ✅ Generated 146 tracks via standard AudioGuide matching
- ✅ RPP opens in Reaper (372 KB)
- ⚠️ **Wave files don't play in RPP** - Need to investigate
- ✅ WAV rendered via Csound (4.9 MB)
- ✅ HTML log shows analysis details

**Files Created**:
```
/Applications/AudioGuide/test_output/
├── cello_baseline.rpp         (372 KB, 146 tracks) ✅ Opens in Reaper
├── cello_baseline.wav          (4.9 MB) ✅ Rendered
├── cello_baseline.csd          (232 KB) Csound score
├── cello_baseline_log.html     (81 KB) Analysis log
├── cello_from_sines.rpp        (15 KB, 6 tracks) ❌ Parsing errors
└── cello_from_sines.wav        (2.4 MB) ✅ But missing fundamental
```

#### Key Learnings

1. **Start with baseline first** - User was correct! Validate existing pipeline before adding features
2. **RPP format is finicky**:
   - PT lines: NO angle brackets (`PT time value shape`, not `<PT ...>`)
   - TAKEENV goes inside ITEM, alongside SOURCE (not inside TAKE)
   - Envelope times must span full item duration (not normalized 0-1)
3. **AudioGuide quirks**:
   - Corpus files need `wholeFile=True` if no .txt segmentation
   - `minFrame=0` causes division by zero in superimpose
   - VERBOSITY=0 needed for non-capable terminals
4. **Python 3.13 compatibility** - Regex bytes/string handling changed

#### RPP TAKEENV Format (Validated)

```
<ITEM
  POSITION 0.000000
  NAME "filename.wav"
  LENGTH 26.718481
  SOFFS 0.000000
  VOLPAN 1.000000 0.0 1.0 -1.0
  <SOURCE WAVE
    FILE "/path/to/file.wav"
  >
  <TAKEENV
    NAME "Volume"
    ACT 1
    VIS 1
    LANEHEIGHT 0 0
    ARM 0
    DEFSHAPE 0 -1 -1
    PT 0.000000 1.000000 0
    PT 26.664064 0.500000 0
  >
>
```

**Critical details**:
- PT times are **absolute project time** (not relative to item)
- PT values are **linear** (1.0 = 0dB, 0.5 = -6dB)
- PT shape: 0 = linear interpolation

#### Current Issues

1. **Wave files don't play in baseline RPP**
   - RPP opens and shows 146 tracks
   - Need to check file paths, sample rate mismatches, or Reaper settings
   
2. **Custom spectral test had bugs**:
   - Envelope timing: used normalized 0-1 instead of absolute seconds
   - PT format: had angle brackets (removed)
   - TAKE wrapper: not needed for simple TAKEENV

3. **Missing fundamental in reconstruction**:
   - Sine corpus is chromatic (semitone steps)
   - Cello f0 at 726 Hz doesn't match exact note
   - Need interpolation or closer frequency tolerance

#### Next Steps

**Immediate** (based on baseline validation):
1. Debug why wave files don't play in Reaper RPP
2. Compare baseline RPP structure to working examples
3. Test if issue is file paths, format, or Reaper settings

**Then - Incremental Enhancement**:
1. Fix spectral test envelope timing bugs
2. Add spectral analysis to baseline AudioGuide config
3. Test TAKEENV with simple static gain first
4. Gradually add time-varying automation
5. Integrate harmonic layering once basics work

**Test Cases**:
- ✅ Baseline: Cello + sine corpus via standard AudioGuide (146 tracks)
- ⚠️ Custom: Spectral reconstruction (needs RPP fixes)
- 🔜 Enhanced: Baseline + TAKEENV automation
- 🔜 Full: Spectral layering with harmonic matching

#### File Locations

**Source Code**:
- `/Applications/AudioGuide/audioguide-claude/` - Enhanced AudioGuide
- `/Applications/AudioGuide/audioguide/` - Original AudioGuide v1.79

**Test Data**:
- Target: `/Users/jonathankawchuk/Documents/Max 9/Packages/Data Knot/media/Musical Examples/Staub-MelodicCello.wav`
- Corpus: `/Users/jonathankawchuk/Documents/Projects/In Progress/Album 3/corpora/Serum_Sine_Short/` (128 sines, 96kHz/24bit)

**Outputs**:
- `/Applications/AudioGuide/test_output/` - All test results

#### Questions for Next Session

1. Why don't wave files play in the baseline RPP? (paths? format?)
2. Should we fix custom test or enhance baseline?
3. What's the priority: TAKEENV working or spectral matching first?
4. How to handle fundamental matching when sine corpus is chromatic?

---
