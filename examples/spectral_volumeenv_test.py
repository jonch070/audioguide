# Spectral Reconstruction Test: VOLUMEENV Time-Varying Automation
# Test the new ENABLE_SPECTRAL_VOLUMEENV feature with track-level volume automation

VERBOSITY = 1

# Target: Single sustained cello note for clear envelope visualization
TARGET = tsf('/Applications/AudioGuide/test_output/cello_Ds2_single_note.wav',
             thresh=-80, offsetRise=0.5)

# Corpus: Optimized pure sine corpus
CORPUS = [
    csf('/Applications/AudioGuide/test_output/spectral_sine_corpus', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION MODE with VOLUMEENV
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = True      # Single spectral snapshot
SPECTRAL_TOLERANCE_CENTS = 100
SPECTRAL_MAX_PARTIALS = 8       # 8 partials to see envelope variation
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.01

# NEW: Enable track-level volume automation
ENABLE_SPECTRAL_VOLUMEENV = True

# Standard options
SEARCH = [spass('closest', d('f0-seg', norm=1))]
SUPERIMPOSE = si(maxSegment=16, maxOverlap=16)
ENABLE_TAKEENV = False

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/spectral_volumeenv_test.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/spectral_volumeenv_test.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/spectral_volumeenv_test_log.html'
