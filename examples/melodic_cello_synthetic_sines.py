# Spectral Reconstruction: Staub-MelodicCello.wav with Synthetic Sine Corpus
# Using the pure sine corpus we created for test_chord

VERBOSITY = 1

# Target: Real melodic cello performance
TARGET = tsf('/Users/jonathankawchuk/Documents/Max 9/Packages/Data Knot/media/Musical Examples/Staub-MelodicCello.wav',
             thresh=-35, offsetRise=0.05, minSegLen=0.1)

# CORPUS: Our synthetic pure sine waves
CORPUS = [
    csf('/Applications/AudioGuide/test_output/spectral_sine_corpus', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION MODE - Optimized settings
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False         # Segment at note changes
SPECTRAL_TOLERANCE_CENTS = 100      # 1 semitone tolerance
SPECTRAL_MAX_PARTIALS = 6           # Fewer partials for clarity (fundamental + 5 harmonics)
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.02 # 2% threshold

# DISABLE VOLUMEENV for Csound compatibility
ENABLE_SPECTRAL_VOLUMEENV = False

# INCLUDE target tracks in RPP (at top, for reference)
RPP_INCLUDE_TARGET = True

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_synthetic_sines.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_synthetic_sines.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_synthetic_sines_log.html'
