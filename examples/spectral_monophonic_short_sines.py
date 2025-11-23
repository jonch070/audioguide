# Spectral Reconstruction Test: Original Short Sine Corpus
# Compare performance with the non-optimized Serum_Sine_Short corpus

VERBOSITY = 1

# Target: Same monophonic cello phrase
TARGET = tsf('/Users/jonathankawchuk/Downloads/cello test/media/cello test_stems_cello test .wav',
             thresh=-35, offsetRise=0.05, minSegLen=0.1)

# Corpus: Original short Serum sine corpus (10ms sustain, 3s decay)
CORPUS = [
    csf('/Users/jonathankawchuk/Documents/Projects/In Progress/Album 3/corpora/Serum_Sine_Short', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION MODE
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False
SPECTRAL_TOLERANCE_CENTS = 100
SPECTRAL_MAX_PARTIALS = 4       # Keep it at 4 for fair comparison
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.01

# Standard options
SEARCH = [spass('closest', d('f0-seg', norm=1))]
SUPERIMPOSE = si(maxSegment=16, maxOverlap=16)
ENABLE_TAKEENV = False

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/spectral_short_sines.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/spectral_short_sines.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/spectral_short_sines_log.html'
