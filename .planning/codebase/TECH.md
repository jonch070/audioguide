# Technology Stack

**Analysis Date:** 2026-02-19

## Languages

**Primary:**
- Python 3.x - All core functionality, CLI tools, and GUI backend

**Secondary:**
- JavaScript - GUI templates (`gui/js/`)
- HTML/CSS - GUI templates

## Runtime

**Environment:**
- Python 3.x (standard library + pip packages)

**Package Manager:**
- Not formally defined (no requirements.txt, setup.py, or pyproject.toml found)
- Dependencies appear to be installed via pip directly

## Frameworks

**Core Audio Processing:**
- NumPy - Array operations, FFT, numerical computing
- SciPy - Signal processing (butter, filtfilt, hilbert, find_peaks)
- soundfile - Audio file I/O

**Optional/Backend:**
- librosa - Pitch detection (PYIN), optional dependency
- FluCoMa (fluid corpus tools) - Segmentation algorithms
- aaf2 - AAF file format output

**GUI:**
- Flask - Web-based GUI backend (`gui/app.py`)

**Testing:**
- No formal test framework detected

**Build/Dev:**
- No formal build system

## Key Dependencies

**Critical:**
- numpy - Core numerical computing for all audio processing
- scipy - Signal processing, FFT, filtering
- soundfile - Audio file reading/writing

**Infrastructure:**
- flask - Web GUI server
- aaf2 - Professional AAF format output

**Optional:**
- librosa - Enhanced pitch detection (gracefully degrades if missing)
- fluid-soundfile - FluCoMa corpus segmentation

## Configuration

**Environment:**
- Configuration via Python options files (loaded via exec())
- Default values in `audioguide/defaults.py` (125 lines)
- No environment variable configuration detected
- No .env files

**Build:**
- No build configuration files found
- No pyproject.toml or setup.py

## Platform Requirements

**Development:**
- Python 3.x
- NumPy, SciPy, soundfile (core)
- librosa (optional, for pitch detection)
- Flask (for GUI)

**Production:**
- Same as development
- CLI usage via agConcatenate.py, agSegmentSf.py, agGranulateSf.py, agGetSfDescriptors.py

---

*Stack analysis: 2026-02-19*
