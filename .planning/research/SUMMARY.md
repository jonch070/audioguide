# Research Summary: AudioGuide Corpus-Based Audio Synthesis

**Domain:** Corpus-Based Audio Synthesis / Concatenative Synthesis
**Researched:** 2026-02-19
**Overall confidence:** MEDIUM-HIGH

## Executive Summary

Corpus-based audio synthesis builds sound by selecting and concatenating segments (grains, notes, slices) from a database of recordings. The architecture follows a well-established pipeline pattern pioneered by IRCAM's CATERPILLAR system: **Input → Segmentation → Analysis → Matching → Synthesis → Output**. AudioGuide, a Python tool forked from Ben Hackbarth's original, implements this architecture with unique features including spectral reconstruction and VOLENV automation.

The current milestone adds FluCoMa descriptor integration, enhanced Reaper output (TAKEENV), and usability improvements. Based on research, the recommended architecture keeps the existing pipeline but isolates descriptor computation to support both librosa and FluCoMa, while enhancing the RPP generation module for the new automation features.

## Key Findings

**Stack:** Python-based with numpy/scipy/soundfile for audio, librosa + FluCoMa for descriptors, Flask for GUI. No fundamental stack changes needed.

**Architecture:** Standard corpus-based pipeline with clear component boundaries. Key enhancement needed: shared descriptor module used by both corpus and target analysis.

**Critical pitfall:** Descriptor mismatch between corpus and target analysis causing silent matching failures. Must use identical descriptor computation for both.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: FluCoMa Descriptor Integration
- Addresses: FEATURES.md - "FluCoMa Descriptor Integration"
- Avoids: PITFALLS.md - "Descriptor Mismatch" by creating shared descriptor module
- Rationale: Descriptors are foundational to matching; must come first

### Phase 2: Enhanced Reaper Output (TAKEENV)
- Addresses: FEATURES.md - "Item Gain Automation (TAKEENV)"
- Avoids: PITFALLS.md - "RPP Generation Fragility" with careful format handling
- Rationale: Builds on existing VOLENV infrastructure; low risk addition

### Phase 3: Usability Improvements
- Addresses: FEATURES.md - "Better Usability/CLI"
- Avoids: Minor pitfalls (progress feedback, error messages)
- Rationale: Non-critical path; doesn't block other features

**Phase ordering rationale:**
- FluCoMa must come before any enhanced matching features — can't match on descriptors we don't compute
- TAKEENV builds on existing VOLENV code — share infrastructure
- Usability can happen in parallel or after core features

**Research flags for phases:**
- Phase 1 (FluCoMa): Needs careful integration testing — verify descriptor matrices compatible
- Phase 2 (TAKEENV): Standard RPP generation, unlikely to need deep research
- Phase 3 (Usability): Standard CLI/web patterns, no research needed

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Well-established Python audio stack; verified current versions |
| Features | MEDIUM | Niche domain with limited competitors; draws from academic papers |
| Architecture | MEDIUM-HIGH | Canonical IRCAM architecture verified across multiple systems |
| Pitfalls | MEDIUM | Based on implementation experience and community discussions |

## Gaps to Address

- **Real-time architecture:** Research didn't deeply cover real-time patterns; not needed for current milestone
- **Neural matching alternatives:** Emerging area (embedding-based matching) not covered; future consideration
- **Cross-platform audio handling:** Limited testing data on edge cases (file format, sample rate)

---

## Research Complete

The architecture research is complete. All four research files have been created:
- `.planning/research/SUMMARY.md` (this file)
- `.planning/research/STACK.md` (already existed)
- `.planning/research/FEATURES.md` (already existed)
- `.planning/research/ARCHITECTURE.md` (new)
- `.planning/research/PITFALLS.md` (new)

Ready for roadmap creation.
