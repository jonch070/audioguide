from audioguide.userclasses import TargetOptionsEntry as tsf
from audioguide.userclasses import CorpusOptionsEntry as csf

VERBOSITY = 1

# Piano chord loop - clearer harmonic content for testing polyphonic analysis
TARGET = tsf('/Users/jonathankawchuk/Music/Cymatics Infinity++/Cymatics - Infinity House Samplepack Pt 2/Instrument Loops/Piano Loops/Cymatics - Piano Loop 17 - 128 BPM Emin.wav',
             thresh=-40,          # Piano has clearer attack
             offsetRise=0.02,     # Faster attack detection for piano
             minSegLen=0.4)       # Segment on chord changes

# Use the sine corpus
CORPUS = [
    csf('/Applications/AudioGuide/test_output/spectral_sine_corpus', wholeFile=True)
]

# Enable spectral reconstruction with polyphonic analysis
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False

# Polyphonic analysis settings
SPECTRAL_POLYPHONIC = True
SPECTRAL_POLYPHONIC_TOLERANCE_CENTS = 50  # Standard tolerance
SPECTRAL_POLYPHONIC_MIN_HARMONICS = 3     # Piano has clear harmonics
SPECTRAL_POLYPHONIC_MAX_VOICES = 6        # Piano chords can have 4-6 notes

# Spectral matching parameters
SPECTRAL_TOLERANCE_CENTS = 100
SPECTRAL_MAX_PARTIALS = 6                 # Piano has fewer upper partials than cello
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.02       # Include quieter harmonics

# Output settings
ENABLE_SPECTRAL_VOLUMEENV = False
RPP_INCLUDE_TARGET = True

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/piano_chords_polyphonic.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/piano_chords_polyphonic.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/piano_chords_polyphonic_log.html'

# Increase output gain to address quiet output
OUTPUT_GAIN_DB = 6.0
