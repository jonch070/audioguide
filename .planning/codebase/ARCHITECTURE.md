# Architecture

**Analysis Date:** 2026-02-19

## Pattern Overview

**Overall:** Command-line audio synthesis tool with Python options file configuration

**Key Characteristics:**
- Options-driven configuration via Python files loaded with exec()
- Modular file output system supporting multiple DAW formats
- Analysis-separation architecture: segment → analyze → match → output
- Two synthesis modes: standard concatenative and spectral reconstruction

## Layers

**Configuration Layer:**
- Purpose: Parse and validate user options from Python config files
- Location: `audioguide/concatenativeclasses.py` (parseOptionsV2 class)
- Contains: Options parsing, validation, default loading
- Depends on: `audioguide/tests.py` (type validation), `audioguide/defaults.py`
- Used by: `audioguide/__init__.py` (main class)

**User API Layer:**
- Purpose: User-facing classes for target/corpus/search configuration
- Location: `audioguide/userclasses.py` (290 lines)
- Contains: TargetOptionsEntry (tsf), CorpusOptionsEntry (csf), SearchPassOptionsEntry (spass), SuperimpositionOptionsEntry (si)
- Depends on: anallinkage, descriptordata, util
- Used by: Configuration layer, end-user options files

**Analysis Layer:**
- Purpose: Audio analysis for target and corpus segmentation
- Location: `audioguide/sfsegment.py` (626 lines)
- Contains: target and corpus segment classes, segmentation logic
- Depends on: numpy, soundfile, descriptor_backends
- Used by: Main execution flow

**Spectral Analysis Layer:**
- Purpose: FFT-based spectral analysis for reconstruction synthesis
- Location: `audioguide/spectralanalysis.py` (437 lines)
- Contains: extract_all_spectral_peaks(), extract_partial_envelopes(), harmonic series extraction
- Depends on: numpy, scipy.signal, librosa (optional)
- Used by: `audioguide/spectrallayering.py`, `audioguide/__init__.py`

**Matching/Concatenation Layer:**
- Purpose: Core synthesis algorithm - match corpus segments to target
- Location: `audioguide/__init__.py` (spectral_concatenate, standard_concatenate methods)
- Contains: Main execution orchestration
- Depends on: All above layers
- Used by: Entry points

**Output Layer:**
- Purpose: Generate output files in various formats
- Location: `audioguide/fileoutput/` (multiple modules)
- Contains:
  - `reaper.py` - REAPER RPP files with VOLENV/TAKEENV automation
  - `csoundinterface.py` - Csound synthesis
  - `musicalwriting.py` - Music notation output
  - `aaf.py` - AAF professional format
  - `html5output.py` - Web visualization
  - `signaldecompose.py` - Signal decomposition
- Depends on: numpy, various format libraries
- Used by: Main execution flow

## Data Flow

**Standard Concatenation:**

1. Parse options file via `parseOptionsV2`
2. Initialize analysis interface (descriptor computation backend)
3. Load and segment target audio (`sfsegment.target`)
4. Compute target descriptors
5. Load and segment corpus audio (`sfsegment.corpus`)
6. Compute corpus descriptors
7. Normalize descriptors
8. For each target segment: search corpus for matches
9. Create output events
10. Write output files (RPP, CSOUND, AAF, etc.)

**Spectral Reconstruction Mode:**

1. Same steps 1-6
2. For each target segment: extract spectral peaks via FFT
3. Match peaks to corpus sine waves by frequency
4. Generate SpectralEvent with gain envelopes
5. Write RPP with VOLENV automation

## Key Abstractions

**Options System:**
- Purpose: Centralized configuration management
- Examples: `audioguide/concatenativeclasses.py`, `audioguide/defaults.py`
- Pattern: Python options file executed via exec(), validated against UserVar_types dict

**Segment:**
- Purpose: Represents a slice of audio (target or corpus)
- Examples: `sfsegment.target`, `sfsegment.corpus`
- Pattern: OO with methods for analysis, segmentation, feature extraction

**Descriptor:**
- Purpose: Audio features (MFCC, pitch, amplitude, etc.)
- Examples: `audioguide/descriptordata.py`, `audioguide/descriptor_backends.py`
- Pattern: Backend-agnostic interface with multiple implementations

## Entry Points

**Main Concatenation:**
- Location: `agConcatenate.py` (48 lines)
- Triggers: CLI invocation with options file path
- Responsibilities: Parse args, create audioguide.main(), execute

**Analysis Tools:**
- `agSegmentSf.py` - Segment audio files
- `agGetSfDescriptors.py` - Compute audio descriptors
- `agGranulateSf.py` - Granular synthesis

## Error Handling

**Strategy:** Custom error function with ASCII art

**Patterns:**
- `util.error(errorType, errorData)` - Prints formatted error and exits
- `util.missing_module(modulename)` - Suggests pip install
- Type validation via `tests.testOption()` in `audioguide/tests.py`

## Cross-Cutting Concerns

**Logging:** Custom printer class in `userinterface.py` with verbosity levels
**Validation:** `tests.py` defines UserVar_types dictionary for option validation
**Authentication:** Not applicable (local CLI tool)

---

*Architecture analysis: 2026-02-19*
