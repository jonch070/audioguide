# AudioGuide Improvements

## What This Is

Python concatenative synthesis tool for audio reconstruction. Users supply target sounds and a corpus of source sounds; AudioGuide matches and layers corpus segments to reconstruct the target. Fork of Ben Hackbarth's original with spectral reconstruction, FluCoMa integration, and usability improvements.

## Core Value

Enable musicians to reconstruct sounds using corpus-based synthesis with minimal friction — whether through spectral partial matching, advanced descriptors, or simplified configuration.

## Requirements

### Validated

- ✓ Spectral reconstruction mode — FFT-based peak detection, partial matching (existing)
- ✓ Whole-file analysis — single segment spectral snapshot (existing)
- ✓ Track-level volume automation (VOLENV) in Reaper output (existing)
- ✓ FluCoMa segmentation — noveltyslice, onsetslice, transientslice (existing)
- ✓ Web GUI (Flask) — basic parameter interface (existing)
- ✓ Pure sine corpus generation (existing)

### Active

- [ ] FluCoMa descriptor integration — MFCCs, spectral shape, loudness analysis
- [ ] Enhanced Reaper item gain mapping — per-item volume control beyond VOLENV
- [ ] Usability improvements — simpler config, better CLI, headless operation
- [ ] Upstream sync mechanism — incorporate Ben Hackbarth's changes

### Out of Scope

- [Real-time synthesis] — non-realtime only, explicitly
- [Mobile app] — web-based only
- [Audio preview in GUI] — complexity vs value

## Context

**Current state:**
- Fork of https://github.com/benhackbarth/audioguide
- Remote `upstream` points to original
- Remote `origin` points to https://github.com/jonch070/audioguide

**Existing codebase:**
- Python 3, numpy/scipy, soundfile
- Descriptor backends: ircam, flucoma, librosa (experimental)
- Output formats: RPP (Reaper), Csound, AAF, JSON
- GUI: Flask web app in `gui/`

**Prior work documented:**
- CLAUDE_PLAN.md — FluCoMa integration strategy
- ROADMAP.md — phased improvement plan
- SPECTRAL_RECONSTRUCTION_CONTEXT.md — spectral mode details

## Constraints

- **[Tech]**: Python 3, depends on numpy/scipy/soundfile
- **[FluCoMa]**: Requires CLI binaries in `audioguide/flucoma-bin/` — not yet built
- **[Ben's repo]**: No formal release process, changes come as commits

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Fork over branch | Preserve history, easy PR path back | ✓ Good |
| Spectral reconstruction | Direct FFT peak matching vs pitch detection | ✓ Working |
| Web GUI over CLI-first | Existing Flask app, broader audience | — Pending validation |
| VOLENV for automation | Track-level automation working | ✓ Good |

---
*Last updated: 2026-02-19 after initialization*
