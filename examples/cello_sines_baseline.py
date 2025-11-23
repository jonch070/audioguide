###########################################################################
## Baseline test: Cello reconstructed from sine corpus using standard  ##
## AudioGuide matching (no spectral reconstruction yet)                 ##
##                                                                       ##
## Run with:                                                             ##
## python3 agConcatenate.py examples/cello_sines_baseline.py            ##
###########################################################################

# Disable fancy terminal output
VERBOSITY = 0

TARGET = tsf('/Users/jonathankawchuk/Documents/Max 9/Packages/Data Knot/media/Musical Examples/Staub-MelodicCello.wav',
             thresh=-30,
             offsetRise=0.01)

CORPUS = [
    csf('/Users/jonathankawchuk/Documents/Projects/In Progress/Album 3/corpora/Serum_Sine_Short', wholeFile=True)  # Treat each sine as one segment
]

# Standard AudioGuide matching by duration, power, and timbre
SEARCH = [
    spass('closest_percent', d('effDur-seg', norm=1), d('power-seg', norm=1), percent=25),
    spass('closest', d('f0-seg', norm=1))  # Match by pitch
]

# Allow layering multiple sines
SUPERIMPOSE = si(
    maxSegment=8,      # Up to 8 layered sounds per target segment
    maxOverlap=8       # Allow 8 overlapping sounds
)

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/cello_baseline.rpp'
RPP_INCLUDE_TARGET = False  # Just corpus
CSOUND_CSD_FILEPATH = '/Applications/AudioGuide/test_output/cello_baseline.csd'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/cello_baseline.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/cello_baseline_log.html'

# Render settings
CSOUND_SR = 48000
CSOUND_PLAY_RENDERED_FILE = False
