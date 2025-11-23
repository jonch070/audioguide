# Spectral Reconstruction Test: Staub-MelodicCello.wav (Real Musical Material)
# Tests spectral reconstruction on actual cello performance

VERBOSITY = 1

# Target: Real melodic cello performance
TARGET = tsf('/Users/jonathankawchuk/Documents/Max 9/Packages/Data Knot/media/Musical Examples/Staub-MelodicCello.wav',
             thresh=-35, offsetRise=0.05, minSegLen=0.1)

# Corpus: Optimized pure sine corpus
CORPUS = [
    csf('/Applications/AudioGuide/test_output/spectral_sine_corpus', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION MODE - Settings for real material
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False         # Segment at note changes
SPECTRAL_TOLERANCE_CENTS = 100      # 1 semitone tolerance
SPECTRAL_MAX_PARTIALS = 8           # Start with fewer partials for clarity
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.02 # 2% threshold

# Enable volume automation
ENABLE_SPECTRAL_VOLUMEENV = True

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_spectral.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_spectral.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_spectral_log.html'
