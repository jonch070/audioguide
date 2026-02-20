---
phase: 03-usability
plan: 02
status: complete
---

## Plan 03-02 Summary: Headless CLI, Error Messages

### Completed Tasks

1. **Headless CLI** (`audioguide/cli.py`)
   - `parse_args()` - argparse-based argument parsing
   - `main()` - CLI entry point with full workflow
   - Supports: --config, --template, --validate-only, --target, --corpus, --output, --verbose, --version
   - Entry point: `python -m audioguide` works

2. **Enhanced Error Messages** (`audioguide/util.py`)
   - Added ERROR_SUGGESTIONS dictionary mapping common errors to fixes
   - Enhanced `error()` function with optional suggestion parameter
   - Added `config_error()` function for config-specific errors
   - Auto-looks up suggestions based on error patterns

3. **CLI Entry Point** 
   - Created `audioguide/__main__.py` for `python -m audioguide`
   - Added `concatenate()` function in `__init__.py`

### Verification Results

```
✓ python -m audioguide --help shows all options
✓ python -m audioguide --version shows "AudioGuide version 1.79"
✓ python -m audioguide --template melody --validate-only works
✓ Error messages include suggestions:
  "File not found: /nonexistent/file.wav
   → Check the file path is correct and the file exists"
```

### Files Created/Modified

- Created: `audioguide/cli.py`
- Created: `audioguide/__main__.py`
- Modified: `audioguide/util.py` (enhanced error handling)
- Modified: `audioguide/__init__.py` (added concatenate function)
