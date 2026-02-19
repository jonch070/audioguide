# Phase 1: FluCoMa Descriptor Integration - Research

**Researched:** 2026-02-19
**Domain:** Audio descriptor extraction using FluCoMa toolkit
**Confidence:** HIGH

## Summary

This phase adds FluCoMa as a descriptor backend alongside existing IRCAM descriptors. FluCoMa provides high-quality audio analysis algorithms (MFCCs, spectral shape, loudness, pitch) that can be used for corpus and target matching.

**Primary recommendation:** Use the existing `python-flucoma` package (PyPI) which wraps the FluCoMa CLI tools, combined with extending the existing `descriptor_backends.py` infrastructure. The existing `flucoma_tools.py` provides a solid foundation that can be leveraged.

Key findings:
- FluCoMa CLI tools must be installed separately from flucoma.org
- python-flucoma package provides Python bindings to CLI tools
- FluCoMaBackend in descriptor_backends.py already exists but only handles pitch
- Existing normalization system (0-1 min-max) can be reused
- Caching architecture uses the existing corpus analysis pipeline

## Standard Stack

### Core Dependencies

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| python-flucoma | Latest (PyPI) | Python bindings to FluCoMa CLI | Official Python package by FluCoMa developer community |
| FluCoMa CLI | 1.0+ | Core audio analysis algorithms | Required dependency - must be installed separately |

### Installation

**FluCoMa CLI Tools (required):**
```bash
# Download from https://www.flucoma.org/download/
# Or build from source: https://github.com/flucoma/flucoma-cli
```

**Python package:**
```bash
pip install python-flucoma
# Or: pip install git+https://github.com/jamesb93/python-flucoma
```

**AudioGuide dependencies already present:**
- numpy, scipy, soundfile (for audio processing)

### FluCoMa Tools for Descriptors

| Tool | Descriptor(s) | AudioGuide Name | Use Case |
|------|---------------|-----------------|----------|
| fluid-mfcc | MFCC coefficients (13 default) | mfcc1-mfcc13 | Timbral matching |
| fluid-spectralshape | centroid, spread, skewness, kurtosis, rolloff, flatness, crest | flucomaspectral_* | Spectral character |
| fluid-loudness | LUFS loudness, true peak | flucomaloudness | Dynamics |
| fluid-pitch | f0 in Hz | flucomapitch | Pitch matching |

## Architecture Patterns

### Recommended Project Structure

```
audioguide/
├── flucoma_tools.py        # [EXISTING] Generic CLI wrappers
├── descriptor_backends.py # [EXISTING] Backend abstraction
│   └── FluCoMaBackend     # [EXTEND] Add full descriptor support
├── flucoma_descriptors.py # [NEW] FluCoMa descriptor integration
├── defaults.py            # [EXTEND] Add FLUC_* configuration options
├── anallinkage.py         # [EXTEND] Register new descriptors
└── descriptordata.py      # [EXTEND] Add normalization for FluCoMa descriptors
```

### Pattern 1: Extending DescriptorBackend

**What:** The existing `DescriptorBackend` abstract base class should be extended to handle full FluCoMa descriptor extraction.

**When to use:** When adding new descriptor backends to AudioGuide.

**Example:**
```python
# Source: Based on existing descriptor_backends.py architecture
class FluCoMaBackend(DescriptorBackend):
    """Extended to support full descriptor extraction"""
    
    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.flucoma_available = self._check_flucoma()
        # Check for individual tools
        self.tools = {
            'mfcc': shutil.which('fluid-mfcc'),
            'spectralshape': shutil.which('fluid-spectralshape'),
            'loudness': shutil.which('fluid-loudness'),
            'pitch': shutil.which('fluid-pitch'),
        }
    
    def analyze_file(self, audio_path, descriptors=None):
        """Extract specified descriptors from audio file.
        
        Args:
            audio_path: Path to audio file
            descriptors: List of descriptor names to extract
                        e.g., ['mfcc', 'spectralshape', 'loudness', 'pitch']
        """
        results = {}
        
        if 'mfcc' in descriptors and self.tools['mfcc']:
            results['mfcc'] = self._extract_mfcc(audio_path)
        
        if 'spectralshape' in descriptors and self.tools['spectralshape']:
            results['spectralshape'] = self._extract_spectralshape(audio_path)
        
        # ... etc
        
        return results
```

### Pattern 2: Descriptor Normalization Integration

**What:** FluCoMa descriptors should integrate with existing 0-1 normalization system.

**When to use:** When FluCoMa descriptors need to be matched against corpus descriptors.

**Example:**
```python
# Source: Based on existing descriptordata.py normalize() method
def normalize_flucoma_descriptors(segment_objs, flucoma_descriptors):
    """Normalize FluCoMa descriptors to 0-1 range.
    
    Uses min-max normalization across all segments.
    """
    for desc_name in flucoma_descriptors:
        # Collect all values across segments
        all_values = []
        for seg in segment_objs:
            values = seg.desc.get(desc_name)
            if values is not None:
                all_values.extend(values)
        
        if all_values:
            min_val = min(all_values)
            max_val = max(all_values)
            
            # Normalize to 0-1
            for seg in segment_objs:
                values = seg.desc.get(desc_name)
                if values is not None:
                    normalized = [(v - min_val) / (max_val - min_val) 
                                  for v in values]
                    seg.desc.set(desc_name + '_normalized', normalized)
```

### Pattern 3: Preset System

**What:** Presets bundle multiple descriptors for common use cases.

**When to use:** When users want quick access to common descriptor combinations.

**Example:**
```python
# Presets for FluCoMa descriptors
FLUCOMA_PRESETS = {
    'timbre': ['mfcc1', 'mfcc2', 'mfcc3', 'mfcc4', 'mfcc5', 
               'flucomaspectral_centroid'],
    'pitch': ['flucomapitch'],
    'loudness': ['flucomaloudness'],
    'harmony': ['flucomapitch', 'mfcc1', 'mfcc2', 'mfcc3', 
                'flucomaspectral_centroid', 'flucomaspectral_flatness'],
    'full': ['mfcc1', 'mfcc2', 'mfcc3', 'mfcc4', 'mfcc5', 'mfcc6', 'mfcc7',
             'mfcc8', 'mfcc9', 'mfcc10', 'mfcc11', 'mfcc12', 'mfcc13',
             'flucomaspectral_centroid', 'flucomaspectral_spread',
             'flucomaspectral_skewness', 'flucomaspectral_kurtosis',
             'flucomaspectral_rolloff', 'flucomaspectral_flatness',
             'flucomaspectral_crest', 'flucomaloudness', 'flucomapitch']
}
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CLI tool invocation | Custom subprocess calls | flucoma_tools.py run_flucoma_tool() | Already exists, handles parameter conversion, error handling |
| MFCC extraction | Custom librosa/scipy implementation | fluid-mfcc | Consistent with other FluCoMa descriptors |
| Spectral analysis | Custom FFT-based descriptors | fluid-spectralshape | 7 descriptors in one tool, professionally implemented |
| Loudness measurement | RMS/peak calculation | fluid-loudness | EBU R128 standard, models human hearing |
| Pitch detection | Autocorrelation/zero-crossing | fluid-pitch | Multiple algorithms (YIN, cepstrum), robust |

**Key insight:** The FluCoMa toolkit is professionally maintained and provides consistent, research-quality audio analysis. Hand-rolling descriptors leads to inconsistency with other analysis pipelines and misses well-tested algorithms.

## Common Pitfalls

### Pitfall 1: CLI Tools Not in PATH
**What goes wrong:** FluCoMa backend fails silently because `fluid-mfcc` etc. aren't found.
**Why it happens:** FluCoMa CLI must be installed separately and added to PATH.
**How to avoid:** Check tool availability on startup, provide clear error message with installation instructions.
**Warning signs:** "Tool not found in PATH" errors, backend falls back to IRCAM.

### Pitfall 2: Descriptor Range Mismatch
**What goes wrong:** FluCoMa descriptors don't match because ranges differ from IRCAM (e.g., MFCCs can be negative).
**Why it happens:** Different normalization approaches between backends.
**How to avoid:** Use 0-1 min-max normalization consistently, document expected ranges.
**Warning signs:** All matches cluster at extreme values, poor matching results.

### Pitfall 3: Caching Invalidation
**What goes wrong:** Changing FluCoMa descriptors doesn't re-analyze corpus.
**Why it happens:** Cache key doesn't include descriptor selection.
**How to avoid:** Include descriptor list/config in cache key.
**Warning signs:** Old descriptor values persist after changing selection.

### Pitfall 4: Frame Rate Mismatch
**What goes wrong:** FluCoMa descriptors have different frame rates than target segments.
**Why it happens:** Default hop size differs from AudioGuide's 0.01024s.
**How to avoid:** Configure FFT settings to match AudioGuide's analysis (0.04096s window, 0.01024s hop).
**Warning signs:** Descriptor arrays have wrong length for segment duration.

### Pitfall 5: Combining FluCoMa with IRCAM Descriptors
**What goes wrong:** Mixing descriptors from different backends produces unexpected results.
**Why it happens:** Different normalization, different scales, different frame rates.
**How to avoid:** Ensure consistent normalization, document mixing behavior, provide warnings.
**Warning signs:** Some descriptors dominate matching due to scale differences.

## Code Examples

### Example 1: Extracting FluCoMa Descriptors

```python
# Source: Based on flucoma_tools.py and FluCoMa documentation
from audioguide.flucoma_tools import run_flucoma_tool
import soundfile as sf
import numpy as np

def extract_flucoma_descriptors(audio_path, descriptors=['mfcc', 'spectralshape', 'loudness', 'pitch']):
    """Extract FluCoMa descriptors from audio file.
    
    Args:
        audio_path: Path to audio file
        descriptors: List of descriptors to extract
        
    Returns:
        Dictionary of descriptor arrays
    """
    results = {}
    
    # Read source audio for metadata
    audio, sr = sf.read(audio_path)
    
    # Extract each descriptor type
    if 'mfcc' in descriptors:
        mfcc_path = '/tmp/mfcc_output.wav'
        run_flucoma_tool('fluid-mfcc', source=audio_path, mfcc=mfcc_path, 
                        numcoeffs=13, fftsettings=[2048, -1, -1])
        mfcc_data, _ = sf.read(mfcc_path)
        results['mfcc'] = mfcc_data  # Shape: (frames, 13)
    
    if 'spectralshape' in descriptors:
        ss_path = '/tmp/spectralshape_output.wav'
        run_flucoma_tool('fluid-spectralshape', source=audio_path, 
                        features=ss_path, fftsettings=[2048, -1, -1])
        ss_data, _ = sf.read(ss_path)
        # Columns: centroid, spread, skewness, kurtosis, rolloff, flatness, crest
        results['spectralshape'] = ss_data
    
    if 'loudness' in descriptors:
        loud_path = '/tmp/loudness_output.wav'
        run_flucoma_tool('fluid-loudness', source=audio_path, features=loud_path)
        loud_data, _ = sf.read(loud_path)
        # Columns: loudness (LUFS), true_peak
        results['loudness'] = loud_data
    
    if 'pitch' in descriptors:
        pitch_path = '/tmp/pitch_output.wav'
        run_flucoma_tool('fluid-pitch', source=audio_path, pitch=pitch_path,
                        algorithm=2, minfreq=80, maxfreq=2000)
        pitch_data, _ = sf.read(pitch_path)
        # Columns: pitch (Hz), confidence
        results['pitch'] = pitch_data
    
    return results
```

### Example 2: Normalization Configuration

```python
# Source: Based on defaults.py and context requirements
# Add to defaults.py or FLUC_* options

# FluCoMa descriptor configuration
FLUCOMA_ENABLE = True  # Enable FluCoMa descriptor extraction
FLUCOMA_DESCRIPTORS = ['mfcc', 'spectralshape', 'loudness', 'pitch']
FLUCOMA_MFCC_COUNT = 13
FLUCOMA_NORMALIZE = True  # 0-1 min-max normalization (default per context)
FLUCOMA_CACHE_CORPUS = True  # Cache corpus descriptors
FLUCOMA_COMBINE_WITH_IRCAM = True  # Allow combining with IRCAM

# Preset configurations
FLUCOMA_PRESET = 'timbre'  # Default: MFCCs + spectral centroid + pitch
```

### Example 3: Integration with Existing Backend System

```python
# Source: Based on descriptor_backends.py architecture
from audioguide.descriptor_backends import DescriptorBackend

class FluCoMaDescriptorBackend(DescriptorBackend):
    """Full FluCoMa descriptor extraction backend."""
    
    def analyze_file(self, audio_path, descriptors=None):
        """Extract descriptors using FluCoMa tools."""
        if descriptors is None:
            descriptors = ['mfcc', 'spectralshape', 'loudness', 'pitch']
        
        results = {}
        
        # Use flucoma_tools convenience functions
        from audioguide.flucoma_tools import extract_mfcc, extract_loudness, extract_pitch
        
        if 'mfcc' in descriptors:
            mfcc_file = extract_mfcc(audio_path, numCoeffs=13)
            mfcc_data, sr = sf.read(mfcc_file)
            results['mfcc'] = mfcc_data
        
        # ... etc
        
        return {
            'descriptors': results,
            'success': True,
            'error': None
        }
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| IRCAM-only descriptors | FluCoMa + IRCAM backends | Phase 1 | More descriptor options, better pitch detection |
| Custom pitch detection | fluid-pitch (YIN algorithm) | Existing flucoma_tools.py | More robust pitch tracking |
| No MFCCs in spectral mode | fluid-mfcc integration | Phase 1 | Better timbre matching |
| Single descriptor backend | Pluggable backends | Existing descriptor_backends.py | Extensible architecture |

**Deprecated/outdated:**
- Zero-crossing pitch detection: Replaced by fluid-pitch YIN algorithm
- RMS-only loudness: Replaced by EBU R128 loudness (models human hearing)

## Open Questions

1. **Descriptor Naming Convention**
   - What we know: Need unique names to avoid collision with IRCAM descriptors
   - What's unclear: `flucomaspectral_centroid` vs `flucoma_centroid` vs `fc_centroid`
   - Recommendation: Use `flucomaspectral_*` prefix for clarity

2. **Caching Strategy Details**
   - What we know: Corpus should be cached, target computed each time (per context)
   - What's unclear: Cache format, invalidation triggers, storage location
   - Recommendation: Use existing AudioGuide cache infrastructure (pickle/shelve)

3. **SpectralShape Sub-descriptors**
   - What we know: 7 descriptors (centroid, spread, skewness, kurtosis, rolloff, flatness, crest)
   - What's unclear: Whether to expose all 7 or bundle as single "spectral shape" descriptor
   - Recommendation: Expose individually for maximum flexibility, plus preset for "all spectral"

## Sources

### Primary (HIGH confidence)
- https://github.com/jamesb93/python-flucoma - Official Python bindings
- https://learn.flucoma.org/reference/mfcc/ - MFCC documentation
- https://learn.flucoma.org/reference/spectralshape/ - SpectralShape documentation
- https://learn.flucoma.org/reference/loudness/ - Loudness documentation
- https://github.com/flucoma/flucoma-cli - CLI source code

### Secondary (MEDIUM confidence)
- https://discourse.flucoma.org/t/python-flucoma/1863 - Community discussion on Python bindings
- https://www.flucoma.org/download/ - Official download page

### Tertiary (LOW confidence)
- Web search for integration patterns (verified against official docs)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - python-flucoma is well-documented, official package
- Architecture: HIGH - Existing descriptor_backends.py provides clear integration pattern
- Pitfalls: MEDIUM - Based on general audio descriptor pitfalls, FluCoMa-specific issues less documented

**Research date:** 2026-02-19
**Valid until:** 2026-03-19 (30 days - FluCoMa is stable, but check for version updates)
