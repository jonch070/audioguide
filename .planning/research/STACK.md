# Stack Research

**Domain:** Corpus-based audio synthesis / Concatenative synthesis
**Researched:** February 19, 2026
**Confidence:** HIGH

## Recommended Stack

### Core Audio Processing

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **numpy** | >=2.0.0 | Array computing, audio buffer manipulation | Standard for numerical computing in Python; 2.x provides significant performance improvements. Audio data represented as numpy arrays throughout. |
| **scipy** | >=1.15.0 | Signal processing (FFT, filtering, statistics) | `scipy.signal` for spectral analysis, `scipy.stats` for descriptor calculations. Version 1.15+ requires Python 3.11+. |
| **soundfile** | >=0.12.0 | Audio file I/O (WAV, FLAC, OGG) | Built on libsndfile; standard for Python audio. Supports 24-bit PCM and 32-bit float. Reads/writes directly to numpy arrays. |

### Feature Extraction & Descriptors

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **librosa** | >=0.11.0 | Audio analysis (MFCC, onset, pitch) | Dominant library for music/audio analysis. 8K+ GitHub stars. Provides MFCC, chroma, onset detection, tempo analysis. Version 0.11.0 released March 2025. |
| **FluCoMa CLI** | Latest | Advanced corpus descriptors (NMF, HPSS, stats) | The standard for corpus-based music research. Must install separately (binary releases). Python bindings via `python-flucoma` package. |

### FluCoMa Integration Details

| Component | Purpose | Installation |
|-----------|---------|--------------|
| **flucoma-cli** | Command-line tools for audio analysis | Download from [flucoma.org](https://flucoma.org/download/) |
| **python-flucoma** | Python bindings (by James Bradbury) | `pip install flucoma` — provides dataclass wrappers around CLI output |

**FluCoMa key algorithms for concatenative synthesis:**
- `FluidBufStats` — per-segment descriptor statistics
- `FluidBufMFCC` / `FluidBufChroma` — spectral features
- `FluidBufPitch` — fundamental frequency tracking
- `FluidBufOnsetSlice` / `FluidBufAmpSlice` — segmentation
- `FluidBufNMF` / `FluidBufHPSS` — source separation

### DAW Integration

| Technology | Purpose | Why Recommended |
|------------|---------|-----------------|
| **REAPER ReaScript API** | Generate .rpp project files | AudioGuide already outputs RPP format; Python can write ReaScript-compatible files directly. No special API needed—just file I/O. |
| **aaf2** | AAF format export | Optional: for interchange with Pro Tools, Nuendo. Low priority unless interoperability needed. |

### Web Interface

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Flask** | >=3.0.0 | Lightweight web framework | Standard for Python web apps. Already in use by AudioGuide GUI. Simple, extensible, well-documented. |
| **werkzeug** | >=3.0.0 | File upload utilities | Comes with Flask; handles secure file uploads. |

### Development & Testing

| Tool | Purpose | Notes |
|------|---------|-------|
| **pytest** | Unit testing | Standard for Python projects |
| **pytest-cov** | Coverage reporting | Optional but recommended |
| **black** | Code formatting | Keep codebase consistent |

## Alternatives Considered

| Category | Recommended | Alternative | When to Use Alternative |
|----------|-------------|-------------|------------------------|
| Audio I/O | soundfile | scipy.io.wavfile | Only if you need zero external dependencies |
| Feature extraction | librosa + custom | pyAudioAnalysis | If you need pre-built classifiers (not typical for concatenative synthesis) |
| Web framework | Flask | FastAPI | If you need async/websocket support for real-time processing |
| Statistical descriptors | scipy.stats | numpy only | Not recommended—scipy provides needed distributions |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **pyaudio** | Primarily for playback/streaming, not analysis | soundfile for file I/O |
| **pydub** | High-level only, limited control for synthesis | soundfile + numpy for precise control |
| **audioread** | Deprecated; librosa.load handles format detection | soundfile directly |
| **matplotlib** (for audio display) | Heavy; only if you need static plots | Consider no visualization or lightweight alternative |

## Installation

```bash
# Core audio processing
pip install numpy>=2.0.0 scipy>=1.15.0 soundfile>=0.12.0

# Feature extraction
pip install librosa>=0.11.0

# FluCoMa (requires separate CLI installation)
# 1. Download from https://flucoma.org/download/
# 2. Add to PATH
pip install flucoma

# Web interface
pip install Flask>=3.0.0 werkzeug>=3.0.0

# Development
pip install pytest pytest-cov black
```

## Stack Patterns by Variant

**If target is monophonic melody:**
- Focus on onset detection + pitch tracking
- Use librosa.onset, librosa.piptrack
- FluCoMa: FluidBufPitch, FluidBufOnsetSlice

**If target is polyphonic/chords:**
- Use spectral analysis (MFCC, chroma) without pitch
- FluCoMa: FluidBufMFCC, FluidBufStats
- Consider NMF for source separation

**If target is sustained/drone:**
- Bypass onset detection (segment by time)
- Use spectral shape descriptors
- FluCoMa: FluidBufSpectralShape, FluidBufLoudness

## Version Compatibility

| Package | Python Version | Notes |
|---------|----------------|-------|
| numpy >=2.0.0 | >=3.11 | As of 2026, numpy 2.x requires Python 3.11+ |
| scipy >=1.15.0 | >=3.11 | SciPy 1.15+ requires Python 3.11+ |
| librosa >=0.11.0 | >=3.8 | Well-maintained, last release March 2025 |
| soundfile >=0.12.0 | >=3.6 | Mature, stable |
| Flask >=3.0.0 | >=3.11 | Flask 3.0 requires Python 3.11+ |

**Note:** If supporting Python 3.10 or earlier, pin to:
- numpy <2.0 (1.26.x series)
- scipy <1.15 (1.14.x series)
- Flask <3.0 (2.x series)

## Sources

- **numpy** — https://pypi.org/project/numpy/ (v2.4.2, January 2026)
- **scipy** — https://pypi.org/project/scipy/ (v1.17.0, January 2026)
- **soundfile** — https://python-soundfile.readthedocs.io/ (v0.13.1)
- **librosa** — https://github.com/librosa/librosa (v0.11.0, March 2025)
- **FluCoMa** — https://flucoma.org/, https://github.com/flucoma/flucoma-core
- **python-flucoma** — https://github.com/jamesb93/python-flucoma
- **REAPER ReaScript** — https://www.reaper.fm/sdk/reascript/reascript.php
- **Flask** — https://pypi.org/project/Flask/ (v3.1.0, 2025)

---

*Stack research for: AudioGuide Corpus-based Audio Synthesis*
*Researched: February 19, 2026*
