# Feature Research

**Domain:** Corpus-Based Audio Synthesis Tools
**Researched:** 2026-02-19
**Confidence:** MEDIUM

*Note: This is a niche academic/creative domain with few commercial products. Research draws from academic papers (Schwarz, Hackbarth), IRCAM's CataRT, FluCoMa ecosystem, and the AudioGuide fork ecosystem. Confidence is MEDIUM due to limited publicly documented feature comparisons.*

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Corpus Loading** | Must be able to load audio files into a searchable corpus | LOW | Typically whole files or segmented. Basic requirement. |
| **Target Audio Input** | Need to specify what sound to reconstruct | LOW | Usually loading an audio file to match against |
| **Segmentation** | Must break audio into manageable units | MEDIUM | Onset detection, amplitude slicing, or manual. Critical for quality. |
| **Descriptor Analysis** | Need mathematical representation of sound | MEDIUM | MFCC, pitch, loudness, spectral shape - the core matching data |
| **Corpus Matching** | Find best corpus segments for target | MEDIUM | k-NN or similar in descriptor space. Core algorithm. |
| **Audio Output** | Must produce listenable result | LOW | WAV, AIFF - basic file output |
| **Basic DAW Export** | Must work with existing workflows | MEDIUM | RPP, AAF, or similar for importing to DAWs |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Spectral Reconstruction** | Match individual partials/harmonics, not overall timbre | HIGH | AudioGuide already has this. Enables additive-style synthesis. Rare in competitors. |
| **Time-Varying Volume Automation** | Envelope per grain/partial, not static gain | MEDIUM | AudioGuide has VOLENV. CataRT has grain envelopes. Rare in basic tools. |
| **FluCoMa Integration** | Modern descriptor set with ML capabilities | MEDIUM | Access to pitch (PYIN), MFCC, loudness, NMF decomposition, etc. |
| **Multiple Descriptor Weighting** | Prioritize different descriptors per use case | LOW | Simple to implement, high user value. |
| **Real-Time Operation** | Live input matching corpus | HIGH | CataRT excels here. Most offline tools (AudioGuide) don't do this. |
| **Spectral Slicing** | Slice at spectral transitions, not just onsets | MEDIUM | FluCoMa's OnsetSlice, NoveltySlice provide this. |
| **Multi-Format Export** | Csound, Max, Bach, AAF, RPP, JSON | LOW-MEDIUM | AudioGuide already supports many. Competitive advantage in workflow flexibility. |
| **GUI for Corpus Exploration** | Visualize and browse corpus | HIGH | CataRT has 2D visualization. Rare in Python tools. |
| **Descriptor Normalization** | Handle different scales across descriptors | LOW | Important for matching quality. |
| **Polyphonic Analysis** | Detect multiple simultaneous voices | HIGH | AudioGuide has SPECTRAL_POLYPHONIC work. Few competitors do this well. |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Automatic Optimal Descriptor Selection** | Users don't know which descriptors to use | Descriptors are musical choices, not math problems. Different descriptors = different artistic results. | Provide presets for common use cases (timbre matching, pitch matching, rhythm matching) |
| **Real-Time Everything** | Sounds impressive | Real-time constraints limit analysis depth. Offline tools can do deeper analysis. | Offer both modes, don't sacrifice quality for speed unless needed |
| **Neural Synthesis Matching** | Modern approach | Neural approaches (diffusion, VAEs) lose direct corpus relationship. Users want to hear their corpus. | Keep concatenative core, optionally offer neural resynthesis as post-process |
| **Fully Automatic Segmentation** | No user input needed | Segmentation is artistic choice. Different segmentations = different results. | Provide sensible defaults + manual override |
| **Infinite Corpus Size** | More options = better | Memory/processing scales poorly. Quality degrades with too many similar options. | Recommend corpus curation, offer filtering |

## Feature Dependencies

```
[Corpus Loading]
    └──requires──> [Descriptor Analysis]
                        └──requires──> [Segmentation]

[Descriptor Analysis]
    └──requires──> [Corpus Matching]

[Corpus Matching]
    └──requires──> [Audio Output]

[FluCoMa Integration] ──enhances──> [Descriptor Analysis]

[Spectral Reconstruction] ──enhances──> [Corpus Matching]
    └──requires──> [Spectral Peak Detection]

[VOLENV Automation] ──enhances──> [Audio Output]
    └──requires──> [Descriptor Envelope Extraction]

[Multi-Format Export]
    └──requires──> [Audio Output]
```

### Dependency Notes

- **Segmentation requires Corpus Loading:** Can't segment without audio to segment
- **Descriptor Analysis requires Segmented Audio:** Descriptors computed per-segment
- **Corpus Matching requires Descriptor Analysis:** Matching happens in descriptor space
- **Spectral Reconstruction enhances Corpus Matching:** Uses spectral peak descriptors instead of (or in addition to) standard descriptors
- **VOLENV requires Envelope Extraction:** Need amplitude envelope data per grain to write automation
- **FluCoMa Integration enhances Descriptor Analysis:** Provides modern, well-maintained descriptor implementations
- **Multi-Format Export requires Audio Output:** All formats are different representations of the same audio events

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [x] **Corpus Loading** — Already works with wholeFile option
- [x] **Segmentation** — Existing onset/amplitude detection + FluCoMa integration
- [x] **Descriptor Analysis** — Existing IRCAM descriptors + FluCoMa integration
- [x] **Corpus Matching** — Existing k-NN matching
- [x] **Basic Audio Output** — Existing WAV render
- [x] **Reaper RPP Export** — Already implemented

**These are table stakes.** AudioGuide already has them. The milestone is enhancement.

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] **Enhanced FluCoMa Descriptors** — Full integration with pitch (PYIN), MFCC, loudness, spectral shape as matching criteria
- [ ] **Item Gain Automation (TAKEENV)** — Per-item clip gain automation in Reaper RPP
- [ ] **Better Usability** — CLI improvements, error messages, documentation

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Real-Time Operation** — Would require significant architecture change
- [ ] **GUI for Corpus Exploration** — Visual 2D or 3D corpus browser
- [ ] **Polyphonic Source Separation** — Separate target into voices before matching
- [ ] **Neural Resynthesis Option** — Post-process with neural vocoder for smoothing

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| FluCoMa Descriptor Integration | HIGH | MEDIUM | P1 |
| TAKEENV (Item Gain Automation) | HIGH | LOW | P1 |
| Better Usability/CLI | MEDIUM | LOW | P1 |
| Enhanced Spectral Descriptors | MEDIUM | MEDIUM | P2 |
| Multi-Descriptor Weighting | MEDIUM | LOW | P2 |
| Polyphonic Analysis | MEDIUM | HIGH | P3 |
| Real-Time Mode | LOW | VERY HIGH | P3 |
| GUI Corpus Explorer | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for this milestone
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | AudioGuide (Current) | CataRT (IRCAM) | The Concatenator | FluCoMa (Raw) |
|---------|---------------------|----------------|------------------|---------------|
| Offline Operation | ✓ | ✗ | ✓ | N/A |
| Real-Time Operation | ✗ | ✓ | ✓ | ✓ |
| Spectral Reconstruction | ✓ | ✗ | ✗ | ✗ |
| VOLENV Automation | ✓ | Grain envelopes | ✗ | N/A |
| FluCoMa Descriptors | Partial | Via MuBu | Partial | ✓ |
| Reaper Export | ✓ | ✗ | ✗ | N/A |
| Max/MSP Export | ✓ | ✓ | ✗ | Via MuBu |
| Csound Export | ✓ | ✗ | ✗ | N/A |
| Multi-Format Export | ✓ | Limited | ✗ | N/A |

**Our Approach:**
- Keep offline, file-based workflow (what AudioGuide does well)
- Enhance with FluCoMa descriptor integration for better matching options
- Add TAKEENV for more precise automation control
- Improve usability without adding GUI complexity
- Spectral reconstruction remains unique differentiator

## Sources

- Schwarz, D. (2007). "Corpus-Based Concatenative Synthesis." IEEE Signal Processing Magazine.
- CataRT Documentation: https://ircam-ismm.github.io/max-msp/catart.html
- FluCoMa Learn Platform: https://learn.flucoma.org/reference/
- Ben Hackbarth's AudioGuide: https://github.com/benhackbarth/audioguide
- "The Concatenator" (2024): Bayesian approach to real-time musaicing
- FluCoMa Discourse: https://discourse.flucoma.org/

---

*Feature research for: Corpus-Based Audio Synthesis*
*Researched: 2026-02-19*
