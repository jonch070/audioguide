# Spectral Reconstruction Test: Single Note (Cello Ds2)
# Pure sine corpus (chromatic C1-B7) reconstructing a single sustained cello note

VERBOSITY = 0

# Target: Single cello Ds2 note (2 seconds)
TARGET = tsf('/Applications/AudioGuide/test_output/cello_Ds2_single_note.wav',
             thresh=-40, offsetRise=0.01)

# Corpus: Pure chromatic sine waves C1-B7
CORPUS = [
    csf('/Applications/AudioGuide/test_output/spectral_sine_corpus', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION MODE
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_TOLERANCE_CENTS = 100  # Chromatic spacing, need wider tolerance
SPECTRAL_MAX_PARTIALS = 12      # Match up to 12th harmonic
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.02  # Include partials down to 2% of max

# Standard options (not used in spectral mode, but required)
SEARCH = [spass('closest', d('f0-seg', norm=1))]
SUPERIMPOSE = si(maxSegment=1, maxOverlap=1)
ENABLE_TAKEENV = False

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/spectral_single_note.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/spectral_single_note.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/spectral_single_note_log.html'
