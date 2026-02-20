# FluCoMa Novelty Slice - Real World Example (threshold=0.4)
#
# This example uses FluCoMa noveltyslice with optimized threshold=0.4
# Comparison to original threshold=0.5:
#   - threshold=0.5: 5 segments (too coarse, missed most note changes)
#   - threshold=0.4: 52 segments (better detection of spectral changes)
#
# Segmentation pre-generated with:
#   python3.13 -c "
#   import sys
#   sys.path.insert(0, '/Applications/AudioGuide/audioguide-claude')
#   from audioguide.flucoma_segmentation import noveltyslice
#   noveltyslice('/Users/jonathankawchuk/Downloads/The Caterpillar Knight/The Caterpillar Knight-005.wav', algorithm=0, threshold=0.4)
#   "

VERBOSITY = 1

# TARGET: Real musical track with FluCoMa novelty slice segmentation
TARGET = tsf(
    '/Users/jonathankawchuk/Downloads/The Caterpillar Knight/The Caterpillar Knight-005.wav',
    segmentationFilepath='/Users/jonathankawchuk/Downloads/The Caterpillar Knight/The Caterpillar Knight-005_flucoma_noveltyslice.txt',
    thresh=-60
)

# CORPUS: Both Philharmonia and SOL string instruments (violin, viola, cello)
CORPUS = [
    csf('/Users/jonathankawchuk/Downloads/philharmonia/cello', wholeFile=True),
    csf('/Users/jonathankawchuk/Downloads/philharmonia/violin', wholeFile=True),
    csf('/Users/jonathankawchuk/Downloads/philharmonia/viola', wholeFile=True),
    csf('/Users/jonathankawchuk/Music/SOL_0.9_HQ/Strings/Violin', wholeFile=True),
    csf('/Users/jonathankawchuk/Music/SOL_0.9_HQ/Strings/Viola', wholeFile=True),
]

# SPECTRAL RECONSTRUCTION MODE
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False
SPECTRAL_POLYPHONIC = True  # Real music is polyphonic (1-4 voices)
SPECTRAL_TOLERANCE_CENTS = 25
SPECTRAL_MAX_PARTIALS = 4  # Track up to 4 simultaneous voices
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.015
SPECTRAL_TRIM_TO_TARGET = False  # Keep natural durations
SPECTRAL_DURATION_TOLERANCE = 2.0  # ±2 seconds for duration matching
SPECTRAL_NO_REPEAT = True  # Each corpus file used only once

# KEY-AWARE MATCHING
SPECTRAL_KEY_AWARE = True
SPECTRAL_KEY_ROOT = 'auto'  # Automatic key detection
SPECTRAL_SCALE_TYPE = 'major'

# USE FLUCOMA BACKEND FOR CORPUS ANALYSIS
DESCRIPTOR_ANALYSIS_TOOL = 'flucoma'

# DISABLE VOLUMEENV
ENABLE_SPECTRAL_VOLUMEENV = False

# INCLUDE target tracks
RPP_INCLUDE_TARGET = True

# Output files (new names to preserve threshold=0.5 version)
RPP_FILEPATH = '/Applications/AudioGuide/test_output/caterpillar_flucoma_threshold04.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/caterpillar_flucoma_threshold04.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/caterpillar_flucoma_threshold04_log.html'
