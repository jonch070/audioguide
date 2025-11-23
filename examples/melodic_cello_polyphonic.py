# Spectral Reconstruction: POLYPHONIC MODE with Trimming
#
# This configuration demonstrates:
# - Polyphonic harmonic grouping (detects 1-4 simultaneous voices per segment)
# - SPECTRAL_TRIM_TO_TARGET feature prevents long corpus sounds from bleeding into next notes
# - Smart onset-based target segmentation (thresh, offsetRise, minSegLen)
# - Pure sine wave corpus for clean spectral reconstruction
#
# SPECTRAL_TRIM_TO_TARGET:
#   True  = Trim corpus sounds to match target segment duration (prevents bleed)
#   False = Use full corpus file duration (default behavior)
#
# AUTOMATIC GAIN NORMALIZATION:
#   Gains are automatically normalized per target segment to prevent clipping.
#   If any partial in a segment would exceed 0dB, all partials in that segment
#   are scaled down proportionally so the loudest reaches exactly 0dB.
#   This ensures no individual track clips while maintaining relative balance.
#
# How to use:
# 1. Change TARGET path to your audio file (line 14)
# 2. Adjust segmentation: thresh=-45 (amplitude), minSegLen=0.5 (minimum segment length)
# 3. Run: python3 agConcatenate.py examples/melodic_cello_polyphonic.py

VERBOSITY = 1

# TARGET SEGMENTATION: Intelligent onset detection that segments every new note
#
# Parameters control how sensitive segmentation is to note onsets:
# - thresh: Amplitude threshold in dB (lower = more sensitive, more segments)
#   Example: thresh=-60 (very sensitive), thresh=-40 (less sensitive)
# - offsetRise: Time in seconds to wait after onset before creating segment (default 0.05)
# - minSegLen: Minimum segment length in seconds (prevents tiny segments)
#   Example: minSegLen=0.1 (shorter notes), minSegLen=1.0 (longer notes only)
#
# Current settings create note-level segments (not fixed windows):
TARGET = tsf('/Users/jonathankawchuk/Downloads/The Caterpillar Knight/The Caterpillar Knight-005.wav',
             thresh=-50,        # Moderate sensitivity to onsets
             offsetRise=0.05,   # 50ms delay after onset
             minSegLen=0.3)     # Minimum 300ms segments (adjust shorter/longer as needed)

# CORPUS: Combined Philharmonia + SOL libraries (never repeat a corpus file)
# AudioGuide will search ALL samples and choose best spectral matches per partial
# Problematic files will be automatically skipped with a warning
CORPUS = [
    csf('/Users/jonathankawchuk/Downloads/philharmonia', wholeFile=True),
    csf('/Users/jonathankawchuk/Music/SOL_0.9_HQ', wholeFile=True)
]

# NOTE: Spectral reconstruction analyzes FULL SPECTRUM of both target and corpus:
# - Target: FFT extracts all spectral peaks (f0 + harmonics), groups into voices
# - Corpus: FFT finds all frequencies in each sample (fundamental + overtones)
# - Matching: For each target partial, finds best corpus frequency within tolerance
# - Result: Reconstructs target using corpus's natural harmonic content

# SPECTRAL RECONSTRUCTION MODE - POLYPHONIC
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False

# Polyphonic analysis settings
SPECTRAL_POLYPHONIC = True                      # Enable polyphonic mode!
SPECTRAL_POLYPHONIC_TOLERANCE_CENTS = 50        # Tolerance for grouping peaks into harmonics
SPECTRAL_POLYPHONIC_MIN_HARMONICS = 3           # Minimum harmonics to identify a voice
SPECTRAL_POLYPHONIC_MAX_VOICES = 4              # Maximum simultaneous voices to detect

# Spectral matching settings
SPECTRAL_TOLERANCE_CENTS = 25                   # Tighter tolerance reduces beating/modulation (was 100)
SPECTRAL_MAX_PARTIALS = 8                       # Partials per voice
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.015            # Minimum partial amplitude
SPECTRAL_TRIM_TO_TARGET = False                 # Don't trim - use natural corpus file length
SPECTRAL_DURATION_TOLERANCE = 0.5               # Only match corpus files within ±0.5 sec of target duration

# Corpus reuse control
SPECTRAL_NO_REPEAT = True                       # Set True to never reuse any corpus file
# SPECTRAL_TIME_SPARSITY = 5.0                  # Uncomment to set minimum seconds before same file can reuse

# Key-aware corpus selection (NEW FEATURE)
# Filters corpus files so only those whose fundamental frequency's note belongs to the specified key
# This creates more harmonic coherence in the output
SPECTRAL_KEY_AWARE = True                       # Set True to enable key-based filtering
SPECTRAL_KEY_ROOT = 'auto'                      # 'auto' = auto-detect, OR specify: C, C#, D, D#, E, F, F#, G, G#, A, A#, B
SPECTRAL_SCALE_TYPE = 'major'                   # Scale: major, minor, dorian, phrygian, lydian, mixolydian, chromatic
# Note: When SPECTRAL_KEY_ROOT = 'auto', the system analyzes all target segments to detect the key
# using the Krumhansl-Schmuckler algorithm. The detected key is used for all corpus matching.

# DISABLE VOLUMEENV for Csound compatibility
ENABLE_SPECTRAL_VOLUMEENV = False

# INCLUDE target tracks in RPP
RPP_INCLUDE_TARGET = True

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/caterpillar_knight_polyphonic.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/caterpillar_knight_polyphonic.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/caterpillar_knight_polyphonic_log.html'
