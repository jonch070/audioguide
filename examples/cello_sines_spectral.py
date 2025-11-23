###########################################################################
## Spectral Reconstruction Test: Cello from sines                       ##
##                                                                       ##
## This test enables spectral reconstruction mode:                      ##
## - Extract harmonics from cello target                                ##
## - Match sine corpus to each harmonic by frequency                    ##
## - Layer sines with gain adjustments to recreate spectrum             ##
##                                                                       ##
## Run with:                                                             ##
## python3 agConcatenate.py examples/cello_sines_spectral.py            ##
###########################################################################

# Disable fancy terminal output
VERBOSITY = 0

TARGET = tsf('/Users/jonathankawchuk/Documents/Max 9/Packages/Data Knot/media/Musical Examples/Staub-MelodicCello.wav',
             thresh=-30,
             offsetRise=0.01)

CORPUS = [
    csf('/Users/jonathankawchuk/Documents/Projects/In Progress/Album 3/corpora/Serum_Sine_Short', wholeFile=True)
]

# ENABLE SPECTRAL RECONSTRUCTION MODE
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_TOLERANCE_CENTS = 50      # Match within 50 cents
SPECTRAL_MAX_PARTIALS = 8          # Match up to 8 harmonics per target segment
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.01  # Ignore very quiet partials

# SEARCH is not used in spectral mode, but we still need to define it
# (AudioGuide may check for it even if not used)
SEARCH = [
    spass('closest', d('f0-seg', norm=1))
]

# Superimposition settings (allows layering multiple harmonics)
SUPERIMPOSE = si(
    maxSegment=16,     # Up to 16 layered sounds per target
    maxOverlap=16      # Allow full overlap
)

# Disable clip gain for initial test (just test matching first)
ENABLE_TAKEENV = False

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/cello_spectral.rpp'
RPP_INCLUDE_TARGET = False
CSOUND_CSD_FILEPATH = '/Applications/AudioGuide/test_output/cello_spectral.csd'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/cello_spectral.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/cello_spectral_log.html'

# Render settings
CSOUND_SR = 48000
CSOUND_PLAY_RENDERED_FILE = False
