---
phase: 02-reaper-takeenv
plan: 01
subsystem: output
tags: [reaper, takeenv, rpp, automation]

# Dependency graph
requires:
  - phase: 01-flucoma-descriptors
    provides: Phase 1 complete, infrastructure ready
provides:
  - TAKEENV_PER_ITEM_GAIN config option
  - TAKEENV chunk writing in RPP output
  - Per-item gain flowing from config to processor
affects: [phase-02-reaper-takeenv]

# Tech tracking
tech-stack:
  added: []
  patterns: [RPP TAKEENV automation format]

key-files:
  created: []
  modified:
    - audioguide/defaults.py - Added TAKEENV_PER_ITEM_GAIN
    - audioguide/fileoutput/reaper.py - Added format_takeenv call
    - audioguide/__init__.py - Wired per-item gain
    - audioguide/tests.py - Registered new config

key-decisions:
  - Used PER_ITEM_GAIN with fallback to STATIC_GAIN for backward compatibility
  - Added TAKE wrapper for TAKEENV (required by Reaper format)
  - Convert absolute times to relative in format_takeenv

patterns-established:
  - "TAKEENV requires TAKE wrapper in RPP structure"
  - "Envelope times must be relative to item position"

duration: 5min
completed: 2026-02-19
---

# Phase 2 Plan 1: TAKEENV Writing + Per-Item Gain

**TAKEENV written to RPP with per-item gain configuration option**

## Performance

- **Duration:** 5 min
- **Started:** 2026-02-19T20:45:00Z
- **Completed:** 2026-02-19T20:50:00Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments
- Added TAKEENV_PER_ITEM_GAIN config option in defaults.py
- Implemented format_takeenv() call in reaper.py write method
- Added TAKE wrapper structure for TAKEENV (required by Reaper)
- Fixed time conversion (absolute to relative) in format_takeenv
- Wired per-item gain from config to takeenv_processor

## Task Commits

1. **Task 1: Add TAKEENV_PER_ITEM_GAIN config option** - `bdbffef` (feat)
2. **Task 2: Call format_takeenv in reaper.py write method** - `236e0fe` (feat)
3. **Task 3: Pass per-item gain to takeenv_processor** - `b6957f8` (feat)

## Files Created/Modified
- `audioguide/defaults.py` - Added TAKEENV_PER_ITEM_GAIN config
- `audioguide/fileoutput/reaper.py` - Added TAKEENV writing with TAKE wrapper
- `audioguide/__init__.py` - Wired per-item gain to processor
- `audioguide/tests.py` - Registered new config option

## Decisions Made
- Used PER_ITEM_GAIN if set (non-zero), falls back to STATIC_GAIN for backward compatibility
- Added TAKE wrapper around SOURCE when TAKEENV is present (required by Reaper format)
- Fixed format_takeenv to convert absolute timeline times to relative times within the take

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Pre-existing NameError in defaults.py (si() not defined) - not introduced by this plan, doesn't affect TAKEENV functionality

## Next Phase Readiness
- Plan 02-02 (ASR envelope configuration) can proceed
- TAKEENV infrastructure complete - writing chunks to RPP

---
*Phase: 02-reaper-takeenv*
*Completed: 2026-02-19*
