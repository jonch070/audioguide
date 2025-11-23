# Spectral Reconstruction: Staub-MelodicCello.wav with Better Segmentation
# Using longer segments and less sensitive threshold

VERBOSITY = 1

# Target: Real melodic cello performance
# ADJUSTED: Higher threshold and longer minimum segment length
TARGET = tsf('/Users/jonathankawchuk/Documents/Max 9/Packages/Data Knot/media/Musical Examples/Staub-MelodicCello.wav',
             thresh=-45,        # Less sensitive (was -35)
             offsetRise=0.05,
             minSegLen=0.5)     # Longer segments (was 0.1)

# CORPUS: Our synthetic pure sine waves
CORPUS = [
    csf('/Applications/AudioGuide/test_output/spectral_sine_corpus', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION MODE
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False         # Segment based on note changes
SPECTRAL_TOLERANCE_CENTS = 100      # 1 semitone tolerance
SPECTRAL_MAX_PARTIALS = 8           # Moderate number of partials
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.015 # Slightly lower threshold

# DISABLE VOLUMEENV for Csound compatibility
ENABLE_SPECTRAL_VOLUMEENV = False

# INCLUDE target tracks in RPP
RPP_INCLUDE_TARGET = True

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_better_seg.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_better_seg.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_better_seg_log.html'
