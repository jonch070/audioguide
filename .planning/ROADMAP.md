# ROADMAP: AudioGuide Improvements

**Project:** AudioGuide Corpus-Based Audio Synthesis  
**Depth:** Standard  
**Phases:** 3  
**Coverage:** 15/15 v1 requirements mapped

---

## Overview

This roadmap delivers three coherent phases that build on the existing spectral reconstruction infrastructure. Each phase targets a distinct capability: FluCoMa descriptor integration for enhanced matching, Reaper output enhancements for volume automation, and usability improvements for better user experience.

---

## Phase 1: FluCoMa Descriptor Integration

**Goal:** Users can compute and use FluCoMa descriptors for corpus and target matching

**Dependencies:** None (foundation phase)

**Requirements:** FLUC-01, FLUC-02, FLUC-03, FLUC-04, FLUC-05, FLUC-06

**Success Criteria:**

1. **MFCC Computation Works** — User can compute MFCCs for corpus segments using FluCoMa and see descriptor values in output

2. **Spectral Shape Descriptors Work** — User can compute spectral centroid, flatness, and skewness for corpus files

3. **Loudness Descriptors Work** — User can compute loudness (LUFS) for corpus and target, usable in matching

4. **Pitch Detection Works** — User can use FluCoMa PYIN for pitch detection, with pitch values available for matching

5. **No Descriptor Mismatch** — Identical descriptor computation is used for corpus and target analysis (verified by test)

6. **Descriptor Selection Works** — User can specify which FluCoMa descriptors to use for matching via configuration

**Plans:**

- [ ] 01-01-PLAN.md — Core FluCoMa descriptor computation (config + backend + normalization)
- [ ] 01-02-PLAN.md — Presets and descriptor selection integration
- [ ] 01-03-PLAN.md — Validation tests and end-to-end verification

---

## Phase 2: Enhanced Reaper Output (TAKEENV)

**Goal:** Users can control item-level volume automation in RPP output

**Dependencies:** Phase 1 (optional - builds on existing VOLENV infrastructure)

**Requirements:** REAP-01, REAP-02, REAP-03, REAP-04

**Success Criteria:**

1. **Per-Item Gain Applied** — User can set per-item gain and hear volume change in Reaper render

2. **TAKEENV Written to RPP** — RPP file contains TAKEENV automation chunks that Reaper recognizes

3. **Envelope Points Configurable** — User can set attack, sustain, release points per item and see automation in Reaper

4. **Track vs Item Volume Separate** — Adjusting track volume does not affect item volume and vice versa

---

## Phase 3: Usability Improvements

**Goal:** Users have better experience configuring and running AudioGuide

**Dependencies:** None (can run parallel to Phase 2)

**Requirements:** USAB-01, USAB-02, USAB-03, USAB-04, USAB-05

**Success Criteria:**

1. **Templates Available** — User can create new project from "single note", "melody", or "chord" template

2. **Headless Mode Works** — User can run AudioGuide from command line without starting web GUI

3. **Error Messages Are Clear** — When configuration is invalid, user sees message explaining what's wrong and how to fix

4. **Config Save/Load Works** — User can save configuration to JSON file and reload it in a new session

5. **Config Validation Works** — User can run validation before execution and see all issues listed

---

## Progress

| Phase | Goal | Requirements | Status |
|-------|------|--------------|--------|
| 1 - FluCoMa | FluCoMa descriptor integration | 6 | Planned (3 plans) |
| 2 - Reaper | Enhanced Reaper output (TAKEENV) | 4 | Pending |
| 3 - Usability | Usability improvements | 5 | Pending |

---

## Coverage

✓ All 15 v1 requirements mapped to phases  
✓ No orphaned requirements  
✓ Each phase has 2-5 observable success criteria

---

*Created: 2026-02-19*
