# Sine Corpus Test: Spectral Reconstruction Using Pure Sine Waves
#
# This test uses REAL audio as target (The Caterpillar Knight) but reconstructs it
# using only PURE SINE WAVES as the corpus. This tests if spectral matching can
# rebuild complex audio using simple building blocks.
#
# Corpus: 48 sine tones covering 4 octaves (C2-B5), chromatic scale
# Target: Real polyphonic audio with multiple voices
# No-repeat: FALSE (allow sine tones to be reused)

VERBOSITY = 1

# TARGET: Original polyphonic audio (The Caterpillar Knight)
TARGET = tsf('/Users/jonathankawchuk/Downloads/The Caterpillar Knight/The Caterpillar Knight-005.wav',
             thresh=-50,        # Moderate sensitivity to onsets
             offsetRise=0.05,   # 50ms delay after onset
             minSegLen=0.3)     # Minimum 300ms segments

# CORPUS: Pure sine wave collection (48 chromatic notes, C2-B5)
CORPUS = [
    csf('/Applications/AudioGuide/test_output/sine_corpus', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION MODE - POLYPHONIC
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False

# Polyphonic analysis settings
SPECTRAL_POLYPHONIC = True                      # Enable polyphonic mode
SPECTRAL_POLYPHONIC_TOLERANCE_CENTS = 50        # Tolerance for grouping peaks
SPECTRAL_POLYPHONIC_MIN_HARMONICS = 3           # Minimum harmonics to identify a voice
SPECTRAL_POLYPHONIC_MAX_VOICES = 4              # Maximum simultaneous voices

# Spectral matching settings
SPECTRAL_TOLERANCE_CENTS = 25                   # Tight tolerance for precise matching
SPECTRAL_MAX_PARTIALS = 8                       # Partials per voice
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.015            # Minimum partial amplitude
SPECTRAL_TRIM_TO_TARGET = True                  # TRIM sine waves to target duration
# SPECTRAL_DURATION_TOLERANCE = 1.0             # Disabled - allow any duration

# Corpus reuse control - ALLOW REPEATS (sine waves will be reused frequently)
SPECTRAL_NO_REPEAT = False                      # Allow sine tones to be reused
# SPECTRAL_TIME_SPARSITY = 5.0                  # Disabled - unlimited reuse

# Key-aware corpus selection - DISABLED for initial test
SPECTRAL_KEY_AWARE = False                      # Disable key filtering (test all matches)
# SPECTRAL_KEY_ROOT = 'auto'                    # Auto-detect key from target
# SPECTRAL_SCALE_TYPE = 'major'                 # Scale type for detection

# DISABLE VOLUMEENV for Csound compatibility
ENABLE_SPECTRAL_VOLUMEENV = False

# INCLUDE target tracks in RPP
RPP_INCLUDE_TARGET = True

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/sine_corpus_reconstruction.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/sine_corpus_reconstruction.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/sine_corpus_reconstruction_log.html'
