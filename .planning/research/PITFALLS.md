# Domain Pitfalls

**Domain:** Corpus-Based Audio Synthesis
**Researched:** 2026-02-19
**Confidence:** MEDIUM

*Note: This is a niche academic/creative domain. Research draws from academic papers (Schwarz, Hackbarth), IRCAM's CataRT, FluCoMa ecosystem, and community discussions. Confidence is MEDIUM due to limited publicly documented pitfall catalogs.*

---

## Critical Pitfalls

Mistakes that cause rewrites or major issues.

### Pitfall 1: Descriptor Mismatch Between Corpus and Target

**What goes wrong:** Using different descriptor implementations or parameters for corpus vs. target analysis, causing matching to fail silently or produce poor results.

**Why it happens:** User doesn't realize descriptors must be computed identically on both corpus and target. Using librosa for corpus and FluCoMa for target (with default parameters) produces incompatible feature spaces.

**Consequences:**
- Matching algorithm finds "closest" matches that sound wrong
- No error thrown — silent failure
- User loses trust in system

**Prevention:**
- Create shared descriptor computation module used by both corpus and target
- Validate descriptor matrix shapes match before matching
- Document descriptor parameter requirements explicitly

**Detection:**
- Check descriptor matrix dimensions before k-NN
- Log descriptor parameters at analysis time
- Add integration test comparing corpus vs. target descriptor statistics

### Pitfall 2: Memory Explosion with Large Corpora

**What goes wrong:** Loading entire corpus audio into memory, combined with large descriptor matrices, causes OOM on moderate corpora.

**Why it happens:** Naive implementation stores all audio as numpy arrays plus descriptor matrices. A 1-hour corpus at 48kHz = 172MB just for audio, plus descriptors.

**Consequences:**
- Process killed by OS
- Can't work with useful corpus sizes
- Forces users to use tiny corpora

**Prevention:**
- Store corpus as file references, not loaded audio
- Load audio only when generating output
- Cache descriptors separately (much smaller than audio)
- Use memory-mapped arrays if needed

**Detection:**
- Monitor memory usage during corpus loading
- Add warning when corpus exceeds reasonable size
- Test with progressively larger corpora

### Pitfall 3: Segmentation/Analysis Order Confusion

**What goes wrong:** Running segmentation AFTER analysis, or computing descriptors on unsegmented audio.

**Why it happens:** Not understanding that descriptors must be computed PER SEGMENT, not on whole files.

**Consequences:**
- Descriptor values are averages over entire file (useless)
- Matching produces identical results for all segments
- Output sounds wrong

**Prevention:**
- Document pipeline explicitly: segment FIRST, then analyze
- Validate segment count > 0 before analysis
- Test with single-segment corpus to catch order bugs

**Detection:**
- Assert segment count after segmentation
- Log descriptor shapes to verify per-segment computation

---

## Moderate Pitfalls

Mistakes that cause delays or technical debt.

### Pitfall 4: Magic Numbers in Matching Algorithm

**What goes wrong:** Hardcoded thresholds, k values, distance weights scattered through code.

**Why it happens:** Quick prototyping leads to values like `k=5`, `threshold=0.3` embedded in matching logic.

**Consequences:**
- Can't tune for different use cases
- Changing one breaks unknown others
- Hard to document for users

**Prevention:**
- All tunable parameters in `defaults.py`
- Use named constants, not magic numbers
- Document reasonable ranges for each parameter

**Detection:**
- Code review for numeric literals in matching
- Add config validation at startup

### Pitfall 5: Incompatible Audio Format Assumptions

**What goes wrong:** Assuming mono, 44.1kHz, 16-bit PCM throughout, then encountering stereo/48kHz/24-bit.

**Why it happens:** Testing only with convenient formats.

**Consequences:**
- Crashes on real corpus files
- Silent conversion to wrong sample rate
- Descriptor values shift with sample rate

**Prevention:**
- Normalize to single format at corpus loading
- Document required/produced formats explicitly
- Handle stereo (sum to mono or keep separate)

**Detection:**
- Add format validation at corpus load
- Log sample rate, channels, bit depth on load

### Pitfall 6: RPP Generation Fragility

**What goes wrong:** RPP format assumptions break with REAPER version changes or edge cases.

**Why it happens:** RPP is semi-documented; specific features (VOLENV, TAKEENV) have limited examples.

**Consequences:**
- Generated projects don't load in REAPER
- Automation doesn't render correctly
- Format errors not caught until open in REAPER

**Prevention:**
- Use most stable RPP features first
- Validate generated RPP before output (basic syntax check)
- Keep RPP generator simple
- Test with actual REAPER

**Detection:**
- Load generated RPP programmatically (if possible) or manually verify
- Version-gate advanced features

---

## Minor Pitfalls

Mistakes that cause annoyance but are fixable.

### Pitfall 7: Missing Corpus File Handling

**What goes wrong:** Corpus references file that was moved/deleted, silently skips or crashes.

**Consequences:** User doesn't know synthesis is incomplete.

**Prevention:** Validate all corpus files exist before analysis.

### Pitfall 8: Progress Feedback Absence

**What goes wrong:** Long operations show no progress, user thinks it's hung.

**Prevention:** Add progress callbacks to all long operations.

### Pitfall 9: Inconsistent Units

**What goes wrong:** Mix of seconds, samples, milliseconds, frames throughout.

**Prevention:** Pick one unit (seconds recommended), convert at boundaries.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| FluCoMa Integration | Descriptor mismatch | Use shared descriptor module for corpus + target |
| Large Corpus Support | Memory explosion | Load file references, not audio |
| RPP Output | Format fragility | Validate output, test in REAPER |
| New Matching Algorithm | Magic numbers | All parameters in defaults.py |
| Multi-format Export | Format assumption | Normalize at load time |

---

## Sources

- Schwarz, D. (2000). "A System for Data-Driven Concatenative Sound Synthesis." DAFx.
- IRCAM CataRT documentation and source code patterns
- FluCoMa Discourse: https://discourse.flucoma.org/
- AudioGuide issue discussions and community feedback
- "The Concatenator" (2024) — practical implementation challenges

---

*Pitfall research for: Corpus-Based Audio Synthesis*
*Researched: 2026-02-19*
