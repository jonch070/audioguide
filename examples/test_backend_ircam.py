# Test Descriptor Backend System - IRCAM Backend
#
# This test validates the pluggable descriptor analysis backend infrastructure
# using the IRCAM backend (which wraps the existing IRCAM descriptor system).
#
# Purpose: Verify backend system works correctly before adding other backends

VERBOSITY = 1

# TARGET: Simple sine melody (quick test)
TARGET = tsf('/Applications/AudioGuide/test_output/sine_melody_c_major.wav',
             thresh=-60,
             offsetRise=0.05,
             minSegLen=0.3)

# CORPUS: Small sine corpus (48 files, fast analysis)
CORPUS = [
    csf('/Applications/AudioGuide/test_output/sine_corpus', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION MODE
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False
SPECTRAL_POLYPHONIC = False
SPECTRAL_TOLERANCE_CENTS = 25
SPECTRAL_MAX_PARTIALS = 1  # F0 only for quick test
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.015
SPECTRAL_TRIM_TO_TARGET = True
SPECTRAL_NO_REPEAT = False

# KEY-AWARE (optional, not critical for backend test)
SPECTRAL_KEY_AWARE = False

# *** TEST THE BACKEND SYSTEM ***
# Don't set DESCRIPTOR_ANALYSIS_TOOL - this uses default IRCAM descriptors
# (Backend system is only needed for alternative backends like FluCoMa)
# DESCRIPTOR_ANALYSIS_TOOL = 'ircam'  # Commented out - use default

# DISABLE VOLUMEENV
ENABLE_SPECTRAL_VOLUMEENV = False

# INCLUDE target tracks
RPP_INCLUDE_TARGET = True

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/test_backend_ircam.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/test_backend_ircam.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/test_backend_ircam_log.html'
