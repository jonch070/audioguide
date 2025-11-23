# Spectral Reconstruction Test: SC Tube Drum Corpus
# Test spectral reconstruction with percussive/tonal drum samples instead of pure sines

VERBOSITY = 1

# Target: Same monophonic cello phrase
TARGET = tsf('/Users/jonathankawchuk/Downloads/cello test/media/cello test_stems_cello test .wav',
             thresh=-35, offsetRise=0.05, minSegLen=0.1)

# Corpus: SC Tube Drum samples (4,321 pitched percussion samples)
CORPUS = [
    csf('/Users/jonathankawchuk/Music/Instruments/Loose Kontakt Libraries/SC Tube Drum/Samples', wholeFile=True)
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
RPP_FILEPATH = '/Applications/AudioGuide/test_output/spectral_tubedrum.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/spectral_tubedrum.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/spectral_tubedrum_log.html'
