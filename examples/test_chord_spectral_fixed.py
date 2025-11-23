# Spectral Reconstruction Test: C Major Chord (FIXED for Csound rendering)
# VOLUMEENV disabled so WAV matches RPP playback

VERBOSITY = 1

# Target: Synthetic C major chord
TARGET = tsf('/Applications/AudioGuide/test_output/test_chord_c_major.wav',
             thresh=-40, offsetRise=0.1)

# Corpus: Optimized pure sine corpus
CORPUS = [
    csf('/Applications/AudioGuide/test_output/spectral_sine_corpus', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION MODE
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = True
SPECTRAL_TOLERANCE_CENTS = 100
SPECTRAL_MAX_PARTIALS = 24
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.02

# DISABLE VOLUMEENV for Csound compatibility
# (Static gain will be baked into VOLPAN instead)
ENABLE_SPECTRAL_VOLUMEENV = False

# ENABLE target tracks in RPP (muted, at top)
RPP_INCLUDE_TARGET = True

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/test_chord_spectral_fixed.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/test_chord_spectral_fixed.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/test_chord_spectral_fixed_log.html'
