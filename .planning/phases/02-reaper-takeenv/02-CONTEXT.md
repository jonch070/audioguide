# Phase 2: Enhanced Reaper Output (TAKEENV) - Context

**Gathered:** 2026-02-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Users can control item-level volume automation in RPP output. This phase extends existing VOLENV (track-level) with TAKEENV (item-level) for per-item gain control.

**Already implemented:**
- ENABLE_TAKEENV config option in defaults.py
- TAKEENV_STATIC_GAIN for static gain offset
- takeenv_processor.py with add_static_takeenv()
- Basic RPP integration via format_takeenv() in reaper.py

**What needs to be completed:**
- Per-item gain configuration (user sets per-item, not global)
- Dynamic envelope extraction from target audio
- Envelope point configuration (attack, sustain, release per item)
- Track vs item volume separation

</domain>

<decisions>
## Implementation Decisions

### Envelope Format
- TAKEENV format: Point-based automation (time, value pairs)
- Two-point envelope (start/end) for static gain
- Future: Multi-point for dynamic envelopes from target analysis

### Configuration
- Use existing ENABLE_TAKEENV and TAKEENV_STATIC_GAIN
- Extend for per-item gain: TAKEENV_PER_ITEM_GAIN or similar
- User can set gain per layer/segment in config

### Integration with VOLENV
- VOLENV is track-level automation (handled separately)
- TAKEENV is item/clip-level (this phase)
- Both can coexist - separate controls

### Envelope Points
- Default: flat (same gain at start and end)
- Configurable: user can set attack, sustain, release times
- Future: dynamic from target amplitude analysis

### Claude's Discretion
- Exact envelope point format in RPP
- How to expose per-item gain in config
- Default envelope shapes

</decisions>

<specifics>
## Specific Ideas

From earlier discussion:
- User wants "item gain mapping" beyond VOLENV
- Wants ability to map target amplitude to item gain
- Per-item control important

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope

</deferred>

---

*Phase: 02-reaper-takeenv*
*Context gathered: 2026-02-19*
