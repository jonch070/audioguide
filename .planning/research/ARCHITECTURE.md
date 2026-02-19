# Architecture Research

**Domain:** Corpus-Based Audio Synthesis
**Researched:** 2026-02-19
**Confidence:** MEDIUM-HIGH

## Standard Architecture

### System Overview

The canonical architecture for corpus-based concatenative synthesis was established by Diemo Schwarz at IRCAM (CATERPILLAR system, 2000-2015) and later adopted by Ben Hackbarth's AudioGuide. The architecture follows a pipeline pattern with clear component boundaries.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                                   │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │  Corpus     │  │   Target    │  │  Config     │                │
│  │  Audio      │  │   Audio     │  │  Parameters │                │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                │
└─────────┼────────────────┼────────────────┼─────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                                   │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │Segmentation │  │ Descriptor  │  │   Target    │                │
│  │             │  │  Analysis   │  │  Analysis   │                │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                │
│         │                │                │                          │
│         ▼                ▼                ▼                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              Corpus Database / Index                          │   │
│  │   (segments + descriptors + audio references)              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│         │                                  │                         │
│         ▼                                  ▼                         │
│  ┌─────────────────────┐    ┌─────────────────────┐               │
│  │  Unit Selection     │    │  Matching Engine    │               │
│  │  (k-NN search)     │◄───│  (descriptor space)│               │
│  └──────────┬──────────┘    └─────────────────────┘               │
│             │                                                       │
│             ▼                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              Synthesis / Concatenation                       │   │
│  │   (event generation + transform + concatenate)              │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                                    │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │  WAV/Audio  │  │  DAW Project│  │  Real-Time  │                │
│  │  Render     │  │  (RPP/JSON) │  │  Stream     │                │
│  └─────────────┘  └─────────────┘  └─────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **Corpus Loader** | Load audio files, validate formats, manage file references | soundfile + numpy buffers |
| **Segmenter** | Divide audio into units (grains, notes, slices) | Onset detection, amplitude threshold, FluCoMa slices |
| **Descriptor Analyzer** | Extract audio features per segment | librosa + custom + FluCoMa CLI |
| **Target Analyzer** | Analyze target audio for matching | Same as descriptor analyzer |
| **Corpus Database** | Store segments, descriptors, metadata | In-memory Python dict/list or HDF5 |
| **Descriptor Index** | Spatial index for fast k-NN search | BallTree (sklearn), FAISS, or brute force |
| **Matching Engine** | Find best corpus segments for target | k-NN with distance weighting |
| **Synthesizer** | Generate events from matches, apply transforms | Event list with gain, pitch, timing |
| **Output Writer** | Render to audio file or DAW project | numpy → WAV, RPP generator |

## Recommended Project Structure

Based on AudioGuide's existing structure and research findings:

```
audioguide/
├── __init__.py              # Main API, concatenative synthesis logic
├── defaults.py               # Configuration constants
├── concatenativeclasses.py   # Core data classes (Corpus, Target, Event)
├── audioanalysis.py          # Basic audio analysis (RMS, onset)
├── spectralanalysis.py       # Spectral reconstruction logic
├── spectrallayering.py      # Spectral matching algorithm
├── descriptors/              # Descriptor extraction
│   ├── __init__.py
│   ├── librosa_descriptors.py
│   └── flucoma_wrapper.py   # FluCoMa CLI integration
├── segmentation/             # Segmentation strategies
│   ├── __init__.py
│   ├── onset_segmentation.py
│   └── flucoma_segmentation.py
├── matching/                 # Unit selection algorithms
│   ├── __init__.py
│   └── knn_matcher.py
├── fileoutput/              # Output format writers
│   ├── __init__.py
│   ├── reaper.py            # RPP generation
│   ├── json_export.py
│   └── audio_render.py
├── cli/                     # Command-line interface
│   └── audioguide.py
├── gui/                     # Flask web interface
│   ├── app.py
│   └── templates/
├── tests/
│   ├── test_*.py
│   └── audioguide_test.py
└── corpora/                 # Default corpus storage
    └── (generated sines)
```

### Structure Rationale

- **`concatenativeclasses.py`**: Central data model — Corpus, Target, Event classes. Single source of truth for what a "segment" is.
- **`audioanalysis.py` / `spectralanalysis.py`**: Core audio processing — kept separate from matching/synthesis for testability.
- **`descriptors/`**: Feature extraction isolated — allows swapping librosa for FluCoMa without touching matching code.
- **`fileoutput/`**: Format-specific output logic isolated — adding new formats (Logic, Cubase) only requires new module here.
- **`matching/`**: Algorithm isolation — k-NN is standard, but allows future alternatives (neural embedding matching).
- **Configuration via `defaults.py`**: Keep all magic numbers in one place for discoverability.

## Architectural Patterns

### Pattern 1: Pipeline (Default)

**What:** Sequential processing through well-defined stages.
**When to use:** Offline batch processing, initial development.
**Trade-offs:**
- Pros: Easy to debug, clear data flow, straightforward optimization
- Cons: No interactivity, full reprocessing on parameter change

```
corpus_audio → segment → analyze → index
                              ↓
target_audio → analyze → match → synthesize → output
```

### Pattern 2: Incremental/Cached

**What:** Cache descriptor results, skip reprocessing unchanged corpus.
**When to use:** Large corpora, iterative exploration.
**Trade-offs:**
- Pros: Fast iteration, practical for large datasets
- Cons: Cache invalidation complexity, storage overhead

```
if cache_exists:
    load_cached_descriptors()
else:
    compute_descriptors()
    save_cache()
```

### Pattern 3: Streaming (Future)

**What:** Real-time unit selection as target audio arrives.
**When to use:** Live performance, interactive installation.
**Trade-offs:**
- Pros: Real-time responsiveness
- Cons: Complexity explosion, latency constraints, limited analysis depth

*Not currently implemented in AudioGuide — would require significant architecture change.*

## Data Flow

### Primary Flow: Offline Synthesis

```
1. User Configuration
   ↓
2. Corpus Loading (soundfile → numpy)
   ↓
3. Segmentation (onset detection / FluCoMa slices)
   ↓
4. Descriptor Analysis (per segment)
   ↓
5. Corpus Index Building (BallTree / direct array)
   ↓
6. Target Loading & Analysis
   ↓
7. Unit Selection (k-NN in descriptor space)
   ↓
8. Event Generation (CorpusEvent list)
   ↓
9. Output Writing (WAV render or RPP file)
```

### Data Models

**CorpusSegment:**
```
- audio: numpy array
- start_time: float (seconds)
- duration: float (seconds)  
- descriptors: dict {descriptor_name: value}
- source_file: str
- source_start: float
```

**TargetSegment:**
```
- audio: numpy array
- start_time: float
- duration: float
- descriptors: dict
```

**CorpusEvent (output):**
```
- corpus_segment: reference
- output_time: float
- duration: float (may be stretched)
- gain: float (linear or dB)
- transposition: float (semitones)
- envelope: Optional[list of (time, gain) points]
```

### State Management

```
Configuration (defaults.py)
    ↓
CorpusState (in-memory)
    ├── segments[]
    ├── descriptor_matrix (numpy)
    └── index (BallTree)
    ↓
MatchingState
    ├── target_descriptors
    └── match_results[]
    ↓
OutputState
    └── events[]
```

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Small corpus (<100 files) | Direct array matching, no index needed |
| Medium corpus (100-10K files) | BallTree index, cached descriptors |
| Large corpus (10K+ files) | FAISS index, chunked processing, descriptor PCA |

### Scaling Priorities

1. **First bottleneck: Descriptor computation**
   - Fix: Cache descriptors to disk (HDF5 or JSON)
   - Parallelize with multiprocessing if needed

2. **Second bottleneck: k-NN search**
   - Fix: BallTree (sklearn) for medium, FAISS for large
   - Reduce descriptor dimensionality if slow

3. **Third bottleneck: Output generation**
   - Fix: Lazy RPP generation, streaming WAV write
   - Defer audio rendering until needed

## Anti-Patterns

### Anti-Pattern 1: Tight Coupling Between Analysis and Matching

**What people do:** Embed descriptor computation directly in matching loop.
**Why it's wrong:** Can't cache, can't swap analyzers, matching is unnecessarily slow.
**Do this instead:** Two-phase: compute all descriptors first, then match against cached data.

### Anti-Pattern 2: Monolithic "process()" Function

**What people do:** Single function handling loading → segmenting → analyzing → matching → outputting.
**Why it's wrong:** Impossible to debug, test, or optimize отдельные этапы.
**Do this instead:** Clear function boundaries with explicit data passing.

### Anti-Pattern 3: In-Memory Audio Storage

**What people do:** Keep all corpus audio in RAM as numpy arrays.
**Why it's wrong:** Limits corpus size to available RAM.
**Do this instead:** Store file references, load on-demand for synthesis (descriptor computation can be cached separately).

### Anti-Pattern 4: Hardcoded Descriptor Names

**What people do:** Match against specific descriptors like `['mfcc', 'pitch']`.
**Why it's wrong:** Can't add new descriptors without code changes.
**Do this instead:** Descriptor-agnostic matching — pass descriptor names as config, match against whatever exists.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **FluCoMa CLI** | Subprocess call → parse JSON output | Must be installed separately; add to PATH |
| **REAPER** | File generation (RPP format) | No API, just file I/O |
| **librosa** | Python library call | Import and use directly |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Corpus Loader ↔ Segmenter | numpy array | Audio passed as array |
| Segmenter ↔ Descriptor Analyzer | Segment list | Each segment has time range |
| Descriptor Analyzer ↔ Matching | Descriptor matrix | numpy array of shape (n_segments, n_descriptors) |
| Matching ↔ Output Writer | Event list | Each event knows its corpus source |

## Build Order Implications

Based on component dependencies, recommend this implementation order:

### Phase 1: Core Pipeline (Already exists)
1. Corpus loading + segmentation → Working
2. Basic descriptor extraction → Working
3. k-NN matching → Working
4. WAV output → Working

### Phase 2: Enhanced Descriptors (FluCoMa)
1. FluCoMa CLI wrapper → Add python-flucoma bindings
2. Integrate FluCoMa descriptors into matching → Replace/add to existing descriptors
3. Validate output quality with new descriptors

### Phase 3: Enhanced Output
1. Add TAKEENV (item gain automation) → Modify RPP generation
2. Test with existing spectral reconstruction
3. Verify VOLENV + TAKEENV together

### Phase 4: Usability
1. CLI improvements
2. Error messages
3. Documentation

**Key dependency:** FluCoMa integration must come before enhanced matching — can't match on descriptors we don't compute yet.

## Sources

- Schwarz, D. (2000). "A System for Data-Driven Concatenative Sound Synthesis." DAFx.
- Schwarz, D. (2015). "The Caterpillar System for Data-Driven Concatenative Sound Synthesis." HAL Archives.
- Hackbarth, B. (2010). "AudioGuide: A Framework for Creative Exploration of Concatenative Sound Synthesis." IRCAM.
- FluCoMa Documentation: https://learn.flucoma.org/
- FluCoMa Architecture Paper: Green, O., et al. (2022). "Architecture about Dancing: Creating a Cross Environment, Cross Domain Framework for Creative Coding Musicians."

---

*Architecture research for: Corpus-Based Audio Synthesis*
*Researched: 2026-02-19*
