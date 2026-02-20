# FluCoMa Novelty Slice Segmentation Example - Cello
#
# This example demonstrates using FluCoMa's noveltyslice for target segmentation
# combined with FluCoMa backend for corpus f0 analysis.
#
# FluCoMa noveltyslice detects spectral changes, making it ideal for detecting
# note changes in melodic material like cello.
#
# To generate the segmentation file, run:
#   python3.13 -c "
#   import sys
#   sys.path.insert(0, '/Applications/AudioGuide/audioguide-claude')
#   from audioguide.flucoma_segmentation import noveltyslice
#   noveltyslice('/Applications/AudioGuide/test_output/cello_melody_test.wav', algorithm=0, threshold=0.4)
#   "

VERBOSITY = 1

# TARGET: Cello melody with FluCoMa novelty slice segmentation
# Segmentation was pre-generated using FluCoMa noveltyslice
TARGET = tsf(
    '/Applications/AudioGuide/test_output/cello_melody_test.wav',
    segmentationFilepath='/Applications/AudioGuide/test_output/cello_melody_test_flucoma_noveltyslice.txt',
    thresh=-60  # This is still used for silence detection
)

# CORPUS: Philharmonia cello samples (whole file mode for variety)
CORPUS = [
    csf('/Users/jonathankawchuk/Downloads/philharmonia/cello', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION MODE
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False
SPECTRAL_POLYPHONIC = False  # Target is monophonic
SPECTRAL_TOLERANCE_CENTS = 25
SPECTRAL_MAX_PARTIALS = 1  # F0 only (monophonic matching)
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.015
SPECTRAL_TRIM_TO_TARGET = True
SPECTRAL_NO_REPEAT = True  # Each cello sample used only once

# KEY-AWARE MATCHING
# Auto-detect key from target and match corpus samples in that key
SPECTRAL_KEY_AWARE = True
SPECTRAL_KEY_ROOT = 'auto'  # Automatic key detection
SPECTRAL_SCALE_TYPE = 'major'  # Target is in C major

# USE FLUCOMA BACKEND FOR CORPUS ANALYSIS
# This uses FluCoMa's fluid-pitch tool for f0 detection instead of IRCAM
DESCRIPTOR_ANALYSIS_TOOL = 'flucoma'

# DISABLE VOLUMEENV
ENABLE_SPECTRAL_VOLUMEENV = False

# INCLUDE target tracks
RPP_INCLUDE_TARGET = True

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/cello_flucoma_noveltyslice.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/cello_flucoma_noveltyslice.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/cello_flucoma_noveltyslice_log.html'
