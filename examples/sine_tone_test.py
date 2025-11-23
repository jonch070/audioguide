# Sine Tone Test: Verify Key Detection with Simple Target
#
# This test uses a pure sine wave melody (C major scale: C, D, E, F, G)
# to verify automatic key detection is working correctly.
#
# Expected result: Should detect C major and only match corpus files with C, D, E, F, G notes

VERBOSITY = 1

# TARGET: Simple sine tone melody in C major (5 notes, 1 second each)
TARGET = tsf('/Applications/AudioGuide/test_output/sine_melody_c_major.wav',
             thresh=-60,        # Sensitive to detect each note
             offsetRise=0.05,
             minSegLen=0.3)     # Minimum 300ms segments

# CORPUS: Combined Philharmonia + SOL libraries (allow repeats for testing)
CORPUS = [
    csf('/Users/jonathankawchuk/Downloads/philharmonia', wholeFile=True),
    csf('/Users/jonathankawchuk/Music/SOL_0.9_HQ', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION - MONOPHONIC MODE (sine tones are monophonic)
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False
SPECTRAL_POLYPHONIC = False                     # Disable polyphonic for pure sine tones

# Spectral matching settings
SPECTRAL_TOLERANCE_CENTS = 25                   # Tight tolerance
SPECTRAL_MAX_PARTIALS = 8                       # Match harmonics (though sine = only fundamental)
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.015
SPECTRAL_TRIM_TO_TARGET = False                 # Use natural corpus file length
SPECTRAL_DURATION_TOLERANCE = 0.5               # Match files within ±0.5 sec of target

# Corpus reuse control - ALLOW REPEATS for this test
SPECTRAL_NO_REPEAT = False                      # Allow files to be reused
# SPECTRAL_TIME_SPARSITY = 5.0                  # Disabled - allow unlimited repetition

# Key-aware corpus selection - AUTO DETECT
SPECTRAL_KEY_AWARE = True                       # Enable key-based filtering
SPECTRAL_KEY_ROOT = 'auto'                      # Auto-detect key (should detect C major)
SPECTRAL_SCALE_TYPE = 'major'                   # Expected scale type

# DISABLE VOLUMEENV for Csound compatibility
ENABLE_SPECTRAL_VOLUMEENV = False

# INCLUDE target tracks in RPP
RPP_INCLUDE_TARGET = True

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/sine_tone_test.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/sine_tone_test.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/sine_tone_test_log.html'
