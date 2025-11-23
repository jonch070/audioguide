# AudioGuide Improvement Plan: Integrating FluCoMa

## 1. Project Overview
AudioGuide is a non-realtime concatenative synthesis program written in Python. It reconstructs a target sound using a corpus of source sounds, offering extensive control over corpus selection, descriptor mapping, and similarity searching. It outputs to various formats, including Csound, AAF, RPP (Reaper projects), and JSON.

## 2. User's Goals for Improvement
The user has expressed a desire for the following improvements:
*   Better analysis of target sounds.
*   Improved corpus structuring.
*   Enhanced timbre matching from layers and pitch accuracy.
*   Better RPP (Reaper Project) generation.
*   Integration of cutting-edge audio technologies, specifically mentioning FluCoMa.

## 3. Current Analysis of AudioGuide's Architecture
Based on the review of `README.md`, `descriptordata.py`, and `sfsegment.py`:

*   **Descriptor Management (`descriptordata.py`):**
    *   Uses a custom `expandable_matrix` for descriptor data.
    *   `descriptor_manager` handles normalization and creation of `sf_segment_descriptors`.
    *   `sf_segment_descriptors` represents descriptors for individual segments, with some on-the-fly calculations (e.g., delta, delta-delta).
    *   Raw descriptors appear to be loaded from an external source (likely IrcamDescriptor, given the `ircamdescriptor-2.8.6` directory).
    *   Current descriptor calculation methods are relatively basic, relying heavily on `numpy` and some `scipy` functions for statistics.
    *   **No FluCoMa integration currently exists.**

*   **Segmentation (`sfsegment.py`):**
    *   `sfsegment` is the base class for sound file segments, managing basic info and linking to `sf_segment_descriptors`.
    *   `corpusSegment` and `targetSegment` extend `sfsegment` with specific attributes.
    *   The `target` class handles target sound segmentation using `segmentationAlgoV2`, which is a power-based onset detection algorithm.
    *   The segmentation method is functional but could be significantly improved with more advanced techniques.
    *   The `target` class also mentions "signal decomposition" and "partials" (`partialanalysis.py`), indicating some existing advanced analysis capabilities, though their full extent and integration with the main synthesis process are unclear.

## 4. Why FluCoMa is the Right Tool
FluCoMa (Fluid Corpus Manipulation) is an open-source project providing tools for digital composition, working with large sound collections, and integrating advanced signal processing and machine learning. It offers:

*   **Specialized Focus:** FluCoMa is purpose-built for corpus-based sound manipulation, directly aligning with AudioGuide's core functionality.
*   **Advanced Analysis:** It provides a rich suite of modern audio descriptors (e.g., MFCCs, spectral shape, loudness, pitch) and machine learning techniques. This will enable a more nuanced understanding of audio, leading to:
    *   **Better Target Analysis:** More accurate and detailed representation of target sound characteristics.
    *   **Improved Corpus Structuring:** More intelligent organization and querying of the sound corpus.
    *   **Enhanced Timbre and Pitch Accuracy:** More sophisticated timbre modeling and precise pitch tracking for better synthesis results.
*   **Robust Segmentation:** FluCoMa includes various advanced slicing algorithms (e.g., `OnsetSlice`, `NoveltySlice`) that can replace or augment AudioGuide's current segmentation, leading to more musically meaningful segment boundaries.

## 5. Proposed FluCoMa Integration Plan

The integration will proceed in the following stages:

1.  **FluCoMa Command-Line Tool Wrapper:**
    *   Develop a new Python module (e.g., `flucoma_wrapper.py`) to encapsulate calls to FluCoMa's command-line executables using Python's `subprocess` module. This will provide a clean API for interacting with FluCoMa.

2.  **Enhanced Descriptor Analysis:**
    *   Modify `descriptordata.py` to utilize the `flucoma_wrapper` for generating a richer set of audio descriptors (MFCCs, loudness, pitch, spectral shape, etc.) for both target and corpus sounds. This will replace or augment the current IrcamDescriptor-based analysis.
    *   The `descriptor_manager` and `sf_segment_descriptors` classes will be updated to handle and store these new descriptors.

3.  **Improved Target Segmentation:**
    *   Update the `target` class in `sfsegment.py` to use FluCoMa's slicing tools (e.g., `OnsetSlice`, `NoveltySlice`) for more accurate and flexible target segmentation. This will replace the existing `segmentationAlgoV2`.

4.  **Advanced Corpus Matching and Timbre Synthesis:**
    *   Leverage the richer FluCoMa descriptors in `simcalc.py` to develop more sophisticated similarity calculation methods.
    *   Explore FluCoMa's machine learning capabilities (e.g., `fluid-learn~`) to build models for timbre matching and layering, addressing the "timbre from layers" goal.
    *   Refine the superimposition logic to make better use of the enhanced descriptor data.

## 6. Current Roadblock: FluCoMa Executables Required

To proceed with this plan, I require the compiled FluCoMa command-line executables. My current environment lacks the necessary build tools (C++ compiler, CMake, Make) to compile them from source.

**User Action Required:**
1.  **Build FluCoMa CLI:** Please build the FluCoMa command-line tools by following the instructions on their GitHub repository: [https://github.com/flucoma/flucoma-cli](https://github.com/flucoma/flucoma-cli).
2.  **Place Executables:** Create a new directory named `flucoma-bin` within `/Applications/AudioGuide/audioguide/audioguide/` and place all the compiled FluCoMa executables into this new directory.

Once these steps are completed, I can resume the integration process.