# Quality Analysis

**Analysis Date:** 2026-02-19

## Code Organization

**Directory Structure:**
```
audioguide/                    # Main package
├── __init__.py               # Main class, execution orchestration (873 lines)
├── concatenativeclasses.py    # Options parsing, core classes (1144 lines - LARGEST)
├── userclasses.py             # User-facing API (tsf, csf, spass, si) (290 lines)
├── defaults.py                # Default configuration values (125 lines)
├── sfsegment.py               # Target/corpus segmentation (626 lines)
├── spectralanalysis.py        # FFT spectral analysis (437 lines)
├── spectrallayering.py        # Spectral matching algorithm (731 lines)
├── descriptor_backends.py     # Audio feature computation (383 lines)
├── descriptordata.py          # Descriptor storage (661 lines)
├── anallinkage.py             # Options handling (628 lines)
├── simcalc.py                 # Similarity calculations (379 lines)
├── partialanalysis.py         # Partial tracking (367 lines)
├── util.py                    # Utilities, error handling (413 lines)
├── userinterface.py           # Logging/output (328 lines)
├── tests.py                   # Option validation (352 lines)
├── dimscaling.py              # Dimensionality scaling (351 lines)
├── fileoutput/               # Output format handlers
│   ├── reaper.py             # REAPER RPP with VOLENV/TAKEENV
│   ├── csoundinterface.py   # Csound output
│   ├── musicalwriting.py     # Music notation
│   ├── aaf.py                # AAF format
│   └── html5output.py        # Web output
├── flucoma_segmentation.py   # FluCoMa integration (481 lines)
├── flucoma_tools.py          # FluCoMa helpers (295 lines)
├── pylib/                    # Third-party libraries (sompy, xamrt)
└── tests/                    # Minimal test directory
    └── aaf_test.py

examples/                      # Usage examples (43 files)
gui/                          # Flask-based web GUI
agConcatenate.py             # Main CLI entry point
agSegmentSf.py               # Segmentation CLI
agGranulateSf.py             # Granular synthesis CLI
agGetSfDescriptors.py        # Descriptor extraction CLI
```

## Naming Conventions

**Files:**
- Python modules: snake_case (e.g., `spectralanalysis.py`, `userclasses.py`)
- CLI scripts: snake_case with `ag` prefix (e.g., `agConcatenate.py`)

**Functions/Classes:**
- Classes: PascalCase (e.g., `parseOptionsV2`, `TargetOptionsEntry`, `SpectralEvent`)
- Functions: Mixed - mostly snake_case, some camelCase
  - snake_case: `extract_all_spectral_peaks()`, `format_volumeenv()`
  - camelCase: `parse_options_file()`, `set_option()`, `testOption()`

**Variables:**
- Mixed convention
  - snake_case: `search_paths`, `corpus_list`
  - camelCase: `opsfileAsString`, `opsfilehead`
- Constants in `defaults.py`: UPPER_SNAKE_CASE

## Code Style

**Formatting:**
- No formatter configured (no black, autopep8, etc.)
- No .prettierrc or .editorconfig detected
- Mixed indentation: some tabs, some spaces (4-space indent common)

**Linting:**
- No linting configuration detected (no .eslintrc, no pylint config)
- No pre-commit hooks

**Docstrings:**
- Minimal - some functions have docstrings, many don't
- Google-style docstrings in newer code (e.g., `spectralanalysis.py`)
- No enforced documentation standard

## Import Organization

**Pattern:**
```python
# Standard library first
import sys, os, datetime
import subprocess

# Third-party imports
import numpy as np
import soundfile as sf

# Local imports (using absolute imports)
import audioguide.util as util
import audioguide.sfsegment as sfsegment
```

**Path Aliases:**
- No path aliases configured (uses explicit `audioguide.` prefix)

## Error Handling

**Patterns:**
- Custom error function: `util.error(errorType, errorData)`
- Module import failures: `util.missing_module(modulename)`
- No try/except blocks in most code
- Options validation via `tests.testOption()` raises errors

**Logging:**
- Custom printer class in `userinterface.py`
- Verbosity levels (0-5 typically)
- HTML log output option

## Testing

**Framework:** None detected
- No pytest, unittest, or tox configuration
- `audioguide/tests/aaf_test.py` exists but is minimal (29 lines, hardcoded paths)
- `audioguide/tests.py` contains option validation only, not unit tests

**Test Files:**
- Located in: `audioguide/tests/`
- Only: `aaf_test.py` (appears to be example code, not actual tests)

**Coverage:** Unknown (no coverage tools configured)

## Security Considerations

**exec() Usage:**
- Options files are loaded using `exec()` in `concatenativeclasses.py`
- Risk: Arbitrary code execution from user-provided options files
- Note: This is by design (options are Python code)

**File Operations:**
- Direct filesystem access without sanitization in some paths
- Temporary files created in system temp directory

## Known Issues

**TODOs/FIXMEs:**
- Found 2 TODOs in `audioguide/pylib/xamrt.py`:
  - Line 592: "TODO better selection than firstest"
  - Line 605: "TODO better selection than firstest"

**Large Files:**
- `concatenativeclasses.py` - 1144 lines (option parsing + core logic)
- `__init__.py` - 873 lines (main orchestration)
- `spectrallayering.py` - 731 lines
- `sfsegment.py` - 626 lines

## Strengths

1. **Modular Output System** - Clean separation of output formats in `fileoutput/`
2. **Flexible Options System** - Python-based config allows complex logic
3. **Multiple Analysis Backends** - Support for different descriptor algorithms
4. **Good Example Coverage** - 43 example files showing various use cases
5. **Graceful Degradation** - librosa optional, fallback implementations

---

*Quality analysis: 2026-02-19*
