# Spectral Reconstruction: FUNDAMENTAL ONLY with Trimming
# Only matches fundamental frequencies (f0), ignoring harmonics

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

# Spectral matching settings - FUNDAMENTAL ONLY
SPECTRAL_TOLERANCE_CENTS = 25
SPECTRAL_MAX_PARTIALS = 1                       # ONLY FUNDAMENTAL (f0)
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.015
SPECTRAL_TRIM_TO_TARGET = True                  # TRIM ENABLED

# Corpus reuse control
SPECTRAL_NO_REPEAT = False                      # Set True to never reuse any corpus file
# SPECTRAL_TIME_SPARSITY = 5.0                  # Uncomment to set minimum seconds before same file can reuse

ENABLE_SPECTRAL_VOLUMEENV = False
RPP_INCLUDE_TARGET = True

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/caterpillar_f0_only_trim.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/caterpillar_f0_only_trim.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/caterpillar_f0_only_trim_log.html'
