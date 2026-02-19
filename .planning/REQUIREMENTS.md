# Requirements: AudioGuide Improvements

**Defined:** 2026-02-19
**Core Value:** Enable musicians to reconstruct sounds using corpus-based synthesis with minimal friction

## v1 Requirements

### FluCoMa Descriptors

- [ ] **FLUC-01**: User can compute MFCCs for corpus segments using FluCoMa
- [ ] **FLUC-02**: User can compute spectral shape descriptors (centroid, flatness, skewness) for corpus
- [ ] **FLUC-03**: User can compute loudness descriptors for corpus and target
- [ ] **FLUC-04**: User can use FluCoMa pitch detection (PYIN) for matching
- [ ] **FLUC-05**: Descriptor computation uses consistent backend for corpus and target (no mismatch)
- [ ] **FLUC-06**: User can select which FluCoMa descriptors to use for matching

### Reaper Enhancements

- [ ] **REAP-01**: User can set per-item gain in RPP output
- [ ] **REAP-02**: User can write TAKEENV (item-level volume automation) to RPP
- [ ] **REAP-03**: User can control volume envelope points (attack, sustain, release per item)
- [ ] **REAP-04**: User can adjust overall track volume separate from item volume

### Usability

- [ ] **USAB-01**: User can create project from predefined templates (single note, melody, chord)
- [ ] **USAB-02**: User can run AudioGuide headless without GUI
- [ ] **USAB-03**: User receives clear error messages with actionable guidance
- [ ] **USAB-04**: User can save configuration to file and reload later
- [ ] **USAB-05**: User can validate configuration before running

## v2 Requirements

### Upstream Sync

- **SYNC-01**: User can add upstream remote for Ben's repo
- **SYNC-02**: User can pull changes from upstream
- **SYNC-03**: User can see which files differ from upstream

### Advanced Features

- **ADV-01**: User can visualize corpus in 2D/3D descriptor space
- **ADV-02**: User can query corpus by example ( hummed melody)
- **ADV-03**: User can export to Ableton Live format

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real-time synthesis | AudioGuide is explicitly offline/non-realtime |
| Neural synthesis | Keeps concatenative core, neural is different tool |
| Mobile app | Web-based only for v1 |
| Auto-descriptor selection | Descriptors are artistic choices, not math problems |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FLUC-01 | Phase 1 | Pending |
| FLUC-02 | Phase 1 | Pending |
| FLUC-03 | Phase 1 | Pending |
| FLUC-04 | Phase 1 | Pending |
| FLUC-05 | Phase 1 | Pending |
| FLUC-06 | Phase 1 | Pending |
| REAP-01 | Phase 2 | Pending |
| REAP-02 | Phase 2 | Pending |
| REAP-03 | Phase 2 | Pending |
| REAP-04 | Phase 2 | Pending |
| USAB-01 | Phase 3 | Pending |
| USAB-02 | Phase 3 | Pending |
| USAB-03 | Phase 3 | Pending |
| USAB-04 | Phase 3 | Pending |
| USAB-05 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-19*
*Last updated: 2026-02-19 after initial definition*
