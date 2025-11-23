# Spectral Reconstruction Test: Monophonic Cello Phrase
# Pure sine corpus (chromatic C1-B7) reconstructing cello melody with segmentation at note changes

VERBOSITY = 1  # Enable logging

# Target: Monophonic cello phrase with normal segmentation
TARGET = tsf('/Users/jonathankawchuk/Downloads/cello test/media/cello test_stems_cello test .wav',
             thresh=-35, offsetRise=0.05, minSegLen=0.1)  # Segment at note changes

# Corpus: Pure chromatic sine waves C1-B7
CORPUS = [
    csf('/Applications/AudioGuide/test_output/spectral_sine_corpus', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION MODE (segmented - one spectral snapshot per note)
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False     # Allow segmentation at note changes
SPECTRAL_TOLERANCE_CENTS = 100  # Chromatic spacing tolerance
SPECTRAL_MAX_PARTIALS = 16      # Match up to 16 partials per segment
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.01  # Include partials down to 1% of max

# Standard options (not used in spectral mode, but required)
SEARCH = [spass('closest', d('f0-seg', norm=1))]
SUPERIMPOSE = si(maxSegment=16, maxOverlap=16)  # Allow multiple partials per segment
ENABLE_TAKEENV = False

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/spectral_monophonic.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/spectral_monophonic.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/spectral_monophonic_log.html'
