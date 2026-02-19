# Phase 1: FluCoMa Descriptor Integration - Context

**Gathered:** 2026-02-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Users can compute and use FluCoMa descriptors (MFCCs, spectral shape, loudness, pitch) for corpus and target matching. This phase adds FluCoMa as a descriptor backend alongside existing IRCAM descriptors.

</domain>

<decisions>
## Implementation Decisions

### Descriptor Selection
- User can select from a list of available FluCoMa descriptors
- Presets available for common use cases
- Meta/preset options like "extract harmony" that bundle multiple descriptors
- Default/common preset: MFCCs + spectral centroid + pitch (standard timbre matching)
- Normalization: Standard 0-1 range (least user error)

### Performance
- Caching strategy: Claude's discretion - corpus cached, target computed each time
- User should be able to change caching behavior if not working

### Configuration
- Configuration approach: Claude's discretion (extend existing or new section)

### Integration
- Additive: FluCoMa adds new options, existing IRCAM descriptors still work
- Users can combine FluCoMa descriptors with IRCAM descriptors simultaneously in same project

### Claude's Discretion
- Exact normalization implementation
- Caching strategy details
- Configuration option naming/structure
- Descriptor weighting defaults

</decisions>

<specifics>
## Specific Ideas

- Meta option "extract harmony" that uses multiple descriptors under the hood
- User wants ability to change caching behavior if not working
- Goal: minimize user error

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope

</deferred>

---

*Phase: 01-flucoma-descriptors*
*Context gathered: 2026-02-19*
