# Spectral Reconstruction: Staub-MelodicCello.wav with Mixed Corpora
# Using diverse timbral sources for spectral reconstruction

VERBOSITY = 1

# Target: Real melodic cello performance
TARGET = tsf('/Users/jonathankawchuk/Documents/Max 9/Packages/Data Knot/media/Musical Examples/Staub-MelodicCello.wav',
             thresh=-35, offsetRise=0.05, minSegLen=0.1)

# CORPUS: Mix of diverse timbral sources
CORPUS = [
    csf('/Users/jonathankawchuk/Documents/Projects/In Progress/Album 3/Corpora/bassoon-keyslaps-corpus-main', wholeFile=True),
    csf('/Users/jonathankawchuk/Documents/Projects/In Progress/Album 3/Corpora/Chest_Hits_Corpus', wholeFile=True),
    csf('/Users/jonathankawchuk/Documents/Projects/In Progress/Album 3/Corpora/RingingRock-Samples-RD', wholeFile=True),
    csf('/Users/jonathankawchuk/Documents/Projects/In Progress/Album 3/Corpora/Serum_Pitch_ADSR_Short', wholeFile=True),
    csf('/Users/jonathankawchuk/Documents/Projects/In Progress/Album 3/Corpora/Serum_Sine_Short', wholeFile=True),
    csf('/Users/jonathankawchuk/Music/Instruments/Jonathans Instruments/JK Kelp Instruments 2/Kelp Horns', wholeFile=True),
    csf('/Users/jonathankawchuk/Music/Instruments/Jonathans Instruments/Jocelyn', wholeFile=True)
]

# SPECTRAL RECONSTRUCTION MODE - Optimized settings
USE_SPECTRAL_RECONSTRUCTION = True
SPECTRAL_WHOLE_FILE = False         # Segment at note changes
SPECTRAL_TOLERANCE_CENTS = 100      # 1 semitone tolerance
SPECTRAL_MAX_PARTIALS = 6           # Fewer partials for clarity (fundamental + 5 harmonics)
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.02 # 2% threshold

# DISABLE VOLUMEENV for Csound compatibility
ENABLE_SPECTRAL_VOLUMEENV = False

# INCLUDE target tracks in RPP (at top, for reference)
RPP_INCLUDE_TARGET = True

# Output files
RPP_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_mixed.rpp'
CSOUND_RENDER_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_mixed.wav'
HTML_LOG_FILEPATH = '/Applications/AudioGuide/test_output/melodic_cello_mixed_log.html'
