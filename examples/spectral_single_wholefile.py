# Spectral Reconstruction Test: Single Note (Whole File Analysis)
# Pure sine corpus (chromatic C1-B7) reconstructing entire cello note as one segment

VERBOSITY = 1  # Enable logging to see what happens

# Target: Use very low threshold to minimize segmentation
TARGET = tsf('/Applications/AudioGuide/test_output/cello_Ds2_single_note.wav',
             thresh=-80, offsetRise=0.5)  # Low threshold, long offsetRise = fewer/longer segments

# Corpus: Pure chromatic sine waves C1-B7
CORPUS = [
    csf('/Applications/AudioGuide/test_output/spectral_sine_corpus', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION MODE
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = True      # Analyze entire target as single spectral snapshot
SPECTRAL_TOLERANCE_CENTS = 100  # Chromatic spacing, need wider tolerance
SPECTRAL_MAX_PARTIALS = 16      # Match up to 16th harmonic for rich sound
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.01  # Include partials down to 1% of max

# Standard options (not used in spectral mode, but required)
SEARCH = [spass('closest', d('f0-seg', norm=1))]
SUPERIMPOSE = si(maxSegment=1, maxOverlap=1)
ENABLE_TAKEENV = False

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/spectral_wholefile.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/spectral_wholefile.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/spectral_wholefile_log.html'
