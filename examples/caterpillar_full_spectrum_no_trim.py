# Spectral Reconstruction: FULL SPECTRUM without Trimming
# Matches all harmonics (8 partials) but uses full corpus file duration

VERBOSITY = 1

TARGET = tsf('/Users/jonathankawchuk/Downloads/The Caterpillar Knight/The Caterpillar Knight-005.wav',
             thresh=-45,
             offsetRise=0.05,
             minSegLen=0.5)

CORPUS = [
    csf('/Users/jonathankawchuk/Downloads/philharmonia', wholeFile=True),
    csf('/Users/jonathankawchuk/Music/SOL_0.9_HQ', wholeFile=True)
]

USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False

# Polyphonic analysis settings
SPECTRAL_POLYPHONIC = True
SPECTRAL_POLYPHONIC_TOLERANCE_CENTS = 50
SPECTRAL_POLYPHONIC_MIN_HARMONICS = 3
SPECTRAL_POLYPHONIC_MAX_VOICES = 4

# Spectral matching settings - FULL SPECTRUM
SPECTRAL_TOLERANCE_CENTS = 25
SPECTRAL_MAX_PARTIALS = 8                       # FULL HARMONICS (8 partials)
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.015
SPECTRAL_TRIM_TO_TARGET = False                 # NO TRIMMING - use full corpus duration
SPECTRAL_DURATION_TOLERANCE = 1.0               # Only match corpus files within ±1 sec of target duration

# Corpus reuse control
SPECTRAL_NO_REPEAT = False                      # Set True to never reuse any corpus file
# SPECTRAL_TIME_SPARSITY = 5.0                  # Uncomment to set minimum seconds before same file can reuse

ENABLE_SPECTRAL_VOLUMEENV = False
RPP_INCLUDE_TARGET = True

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/caterpillar_full_no_trim.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/caterpillar_full_no_trim.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/caterpillar_full_no_trim_log.html'
