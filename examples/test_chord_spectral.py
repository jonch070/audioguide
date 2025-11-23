# Spectral Reconstruction Test: C Major Chord (Polyphonic Target)
# Tests spectral reconstruction on a synthetic 3-note chord (C4, E4, G4)

VERBOSITY = 1

# Target: Synthetic C major chord
TARGET = tsf('/Applications/AudioGuide/test_output/test_chord_c_major.wav',
             thresh=-40, offsetRise=0.1)

# Corpus: Optimized pure sine corpus
CORPUS = [
    csf('/Applications/AudioGuide/test_output/spectral_sine_corpus', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION MODE - Polyphonic settings
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = True          # Analyze entire chord as one snapshot
SPECTRAL_TOLERANCE_CENTS = 100       # 1 semitone tolerance
SPECTRAL_MAX_PARTIALS = 24          # 3 notes × 8 harmonics each = 24 partials
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.02  # 2% threshold

# Enable volume automation
ENABLE_SPECTRAL_VOLUMEENV = True

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/test_chord_spectral.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/test_chord_spectral.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/test_chord_spectral_log.html'
