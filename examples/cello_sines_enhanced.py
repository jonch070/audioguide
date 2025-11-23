###########################################################################
## Enhanced test: Cello from sines with TAKEENV automation             ##
##                                                                       ##
## Builds on baseline but adds:                                         ##
## 1. Simple TAKEENV with static gain (proof of concept)                ##
## 2. More aggressive layering (match harmonics)                        ##
##                                                                       ##
## Run with:                                                             ##
## python3 agConcatenate.py examples/cello_sines_enhanced.py            ##
###########################################################################

# Disable fancy terminal output
VERBOSITY = 0

TARGET = tsf('/Users/jonathankawchuk/Documents/Max 9/Packages/Data Knot/media/Musical Examples/Staub-MelodicCello.wav',
             thresh=-30,
             offsetRise=0.01)

CORPUS = [
    csf('/Users/jonathankawchuk/Documents/Projects/In Progress/Album 3/corpora/Serum_Sine_Short', wholeFile=True)
]

# Enhanced matching: Select corpus sounds for fundamental + harmonics
# Strategy: Use percent to narrow by approximate frequency region,
# then closest match within that region
SEARCH = [
    # First pass: Narrow to sounds within 2 octaves
    spass('closest_percent', d('f0-seg', norm=1), percent=50),
    # Second pass: Closer frequency match
    spass('closest_percent', d('f0-seg', norm=1), percent=10),
    # Final pass: Best match
    spass('closest', d('f0-seg', norm=1))
]

# Aggressive layering for harmonic reconstruction
SUPERIMPOSE = si(
    maxSegment=16,     # Up to 16 layered sounds per target
    maxOverlap=16      # Allow full overlap
)

# Enable TAKEENV automation in RPP export
# This will be picked up by our enhanced reaper.py
ENABLE_TAKEENV = True          # NEW: Enable clip gain automation
TAKEENV_STATIC_GAIN = -3.0     # NEW: Static gain offset in dB (per layer)

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/cello_enhanced.rpp'
RPP_INCLUDE_TARGET = False
CSOUND_CSD_FILEPATH = '/Applications/AudioGuide/test_output/cello_enhanced.csd'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/cello_enhanced.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/cello_enhanced_log.html'

# Render settings
CSOUND_SR = 48000
CSOUND_PLAY_RENDERED_FILE = False
