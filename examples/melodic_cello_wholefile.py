# Spectral Reconstruction: Staub-MelodicCello.wav - WHOLE FILE MODE
# Testing with entire file as one segment to avoid over-segmentation

VERBOSITY = 1

# Target: Real melodic cello performance
TARGET = tsf('/Users/jonathankawchuk/Documents/Max 9/Packages/Data Knot/media/Musical Examples/Staub-MelodicCello.wav',
             thresh=-35, offsetRise=0.05, minSegLen=0.1)

# CORPUS: Our synthetic pure sine waves
CORPUS = [
    csf('/Applications/AudioGuide/test_output/spectral_sine_corpus', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION MODE - WHOLE FILE (no segmentation)
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = True          # Treat entire file as one segment
SPECTRAL_TOLERANCE_CENTS = 100      # 1 semitone tolerance
SPECTRAL_MAX_PARTIALS = 12          # More partials for richer reconstruction
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.01 # Lower threshold to capture more harmonics

# DISABLE VOLUMEENV for Csound compatibility
ENABLE_SPECTRAL_VOLUMEENV = False

# INCLUDE target tracks in RPP (at top, for reference)
RPP_INCLUDE_TARGET = True

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_wholefile.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_wholefile.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_wholefile_log.html'
