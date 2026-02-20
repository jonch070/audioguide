# FluCoMa Integrated Segmentation Example - Cello
#
# This example demonstrates the NEW integrated FluCoMa segmentation.
# No need to pre-generate segmentation files - just set segmentationMethod!
#
# Usage:
#   python3.13 /Applications/AudioGuide/audioguide-claude/audioguide.py \
#       /Applications/AudioGuide/audioguide-claude/examples/cello_flucoma_integrated.py

VERBOSITY = 1

# TARGET: Cello melody with FluCoMa novelty slice segmentation
# The segmentation happens automatically during target analysis!
TARGET = tsf(
    '/Applications/AudioGuide/test_output/cello_melody_test.wav',
    # NEW: Integrated FluCoMa segmentation - no pre-generation needed!
    segmentationMethod='flucoma_noveltyslice',
    segmentationParams={
        'algorithm': 0,      # 0=spectrum, 1=mfcc, 2=chroma
        'threshold': 0.25,   # Lower threshold for melodic content
    },
    minSegLen=0.1,   # Minimum segment length in seconds
    maxSegLen=10,    # Maximum segment length in seconds
    thresh=-60       # Still used for silence detection
)

# CORPUS: Philharmonia cello samples
CORPUS = [
    csf('/Users/jonathankawchuk/Downloads/philharmonia/cello', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION MODE
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False
SPECTRAL_POLYPHONIC = False  # Target is monophonic
SPECTRAL_TOLERANCE_CENTS = 25
SPECTRAL_MAX_PARTIALS = 1
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.015
SPECTRAL_TRIM_TO_TARGET = True
SPECTRAL_NO_REPEAT = True

# KEY-AWARE MATCHING
SPECTRAL_KEY_AWARE = True
SPECTRAL_KEY_ROOT = 'auto'
SPECTRAL_SCALE_TYPE = 'major'

# USE FLUCOMA BACKEND FOR CORPUS ANALYSIS
DESCRIPTOR_ANALYSIS_TOOL = 'flucoma'

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/cello_flucoma_integrated.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/cello_flucoma_integrated.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/cello_flucoma_integrated_log.html'
RPP_INCLUDE_TARGET = True
ENABLE_SPECTRAL_VOLUMEENV = False
