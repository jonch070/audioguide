# Spectral Reconstruction: Staub-MelodicCello.wav with Sine Corpus
# Simplified version using just sine waves to verify approach

VERBOSITY = 1

# Target: Real melodic cello performance
TARGET = tsf('/Users/jonathankawchuk/Documents/Max 9/Packages/Data Knot/media/Musical Examples/Staub-MelodicCello.wav',
             thresh=-35, offsetRise=0.05, minSegLen=0.1)

# CORPUS: Simple sine waves for clarity
CORPUS = [
    csf('/Users/jonathankawchuk/Documents/Projects/In Progress/Album 3/Corpora/Serum_Sine_Short', wholeFile=True)
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
RPP_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_sines.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_sines.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_sines_log.html'
