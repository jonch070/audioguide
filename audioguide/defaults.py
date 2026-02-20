# Import userclasses needed for default values
from audioguide.userclasses import SuperimpositionOptionsEntry as si
from audioguide.userclasses import TargetOptionsEntry as tsf
from audioguide.userclasses import CorpusOptionsEntry as csf
from audioguide.userclasses import SearchPassOptionsEntry as spass
from audioguide.userclasses import Score as score
from audioguide.userclasses import Instrument as instr

##############  OUTPUT FILES  #############
OUTPUT_FILE_PREFIX = '' # a string
CSOUND_CSD_FILEPATH = 'output/output.csd'
CSOUND_SCORE_FILEPATH = None # 'output/output.score.txt'
CSOUND_RENDER_FILEPATH = 'output/output.aiff'
HTML_LOG_FILEPATH = 'output/log.html'
TARGET_SEGMENT_LABELS_FILEPATH = 'output/targetlabels.txt'
TARGET_SEGMENTATION_GRAPH_FILEPATH = None #'output/targetlabels.jpg'
OUTPUT_LABEL_FILEPATH = 'output/outputlabels.txt'
LISP_OUTPUT_FILEPATH = None #'output/output.lisp.txt'
DATA_FROM_SEGMENTATION_FILEPATH = None #'output/datafromsegmentation.txt'
DICT_OUTPUT_FILEPATH = 'output/output.json'
MAXMSP_OUTPUT_FILEPATH = 'output/output.maxmsp.json'
BACH_FILEPATH = 'output/bachroll.txt'
AAF_FILEPATH = None # 'output/test.aaf'
RPP_FILEPATH = None # 'output/test.rpp'
COPY_OPTIONS_FILEPATH = None
TARGET_DESCRIPTORS_FILEPATH = None # 'output/targetdescriptors.json'
TARGET_PLOT_DESCRIPTORS_FILEPATH = None #'output/targetplot.jpg'
CORPUS_SEGMENTED_FEATURES_JSON_FILEPATH = None

##########  CORPUS   #######
SEARCH = []
CORPUS_GLOBAL_ATTRIBUTES = {}
VOICE_PATTERN = []
VOICE_TO_ONSET_MAPPING = []
ROTATE_VOICES = False
ORDER_CORPUS_BY_DESCRIPTOR = None
RESTRICT_CORPUS_SELECT_PERCENTAGE_BY_STRING = {}
RESTRICT_CORPUS_OVERLAP_BY_STRING = {}

##########  INSTRUMENTS   #######
INSTRUMENTS = None

#######  NORMALIZATION  #######
NORMALIZATION_METHOD = 'standard'
NORMALIZATION_DELTA_FREEDOM = 0 # 0=default stddev
CLUSTER_MAPPING = {}

#######  CONCATENATE SELECTION  #######
SUPERIMPOSE = si()
ALWAYS_MAKE_COMPLETE_MATCHING_RESULTS = False
OUTPUT_GAIN_DB = 0.
RANDOM_SEED = None

#######  POST-CONCATENATION EVENT MANIPULATION  #######
OUTPUTEVENT_ALIGN_PEAKS = False 
OUTPUTEVENT_TIME_STRETCH = 1.
OUTPUTEVENT_TIME_ADD = 0.
OUTPUTEVENT_QUANTIZE_TIME_INTERVAL = 0.25
OUTPUTEVENT_QUANTIZE_TIME_METHOD = None # snapToGrid | medianAggregate
OUTPUTEVENT_DURATION_SELECT = 'cps' # cps | tgt
OUTPUTEVENT_DURATION_MIN = None
OUTPUTEVENT_DURATION_MAX = None
OUTPUTEVENT_CLASSIFY = {'numberClasses': 0, 'descriptors': ['mfcc1-seg', 'mfcc2-seg', 'mfcc3-seg', 'mfcc4-seg']} # only classifies if numberClasses >= 2

############  CSOUND RENDERING  ############
CSOUND_SR = 48000
CSOUND_KSMPS = 128
CSOUND_BITS = 16
CSOUND_CHANNEL_RENDER_METHOD = "corpusmax" # corpusmax | stereo | targetoutputmix | oneChannelPerVoice | oneChannelPerOverlap
CSOUND_STRETCH_CORPUS_TO_TARGET_DUR = None # None | transpose | pv
CSOUND_PLAY_RENDERED_FILE = True
CSOUND_NORMALIZE = False
CSOUND_NORMALIZE_PEAK_DB = -3

##########  BACH   #######
BACH_INCLUDE_TARGET = True
BACH_TARGET_STAFF = 'F'
BACH_CORPUS_STAFF = 'FG'
BACH_DB_TO_VELOCITY_BREAKPOINTS = [-80, 0, -0, 127]
BACH_SLOTS_MAPPING = {1: 'fullpath', 2: 'sfskiptime', 3: 'sfchannels', 4: 'env', 5: 'transposition', 6: 'selectionnumber', 20: 'instr_dynamic', 22: 'instr_articulation', 23: 'instr_notehead', 24: 'instr_annotation', 25: 'instr_technique', 26: 'instr_temporal_mode'}

###########  AAF   ########
AAF_INCLUDE_TARGET = False
AAF_CPSTRACK_METHOD = 'cpsidx'
AAF_AUTOLAUNCH = False

###########  RPP   ########
RPP_INCLUDE_TARGET = False
RPP_CPSTRACK_METHOD = 'cpsidx'
RPP_TRANS_AFFECTS_SPEED = True
RPP_AUTOLAUNCH = False
# TAKEENV clip gain automation
ENABLE_TAKEENV = False  # Enable clip gain automation (TAKEENV)
TAKEENV_STATIC_GAIN = 0.0  # Static gain offset in dB (per layer)
TAKEENV_PER_ITEM_GAIN = 0.0  # Per-item gain offset in dB (alternative to static gain)
# ASR envelope settings for TAKEENV (attack-sustain-release)
TAKEENV_ASR_ATTACK = 0.0  # Attack time in seconds (0 = instant)
TAKEENV_ASR_SUSTAIN = 1.0  # Sustain level as ratio 0-1 (1 = full gain)
TAKEENV_ASR_RELEASE = 0.0  # Release time in seconds (0 = instant)

################  DESCRIPTOR COMPUTATION SETTINGS  ################
DESCRIPTOR_DATABASE_SIZE_LIMIT = 1
DESCRIPTOR_DATABASE_AGE_LIMIT = 7
DESCRIPTOR_OVERRIDE_DATA_PATH = None
DESCRIPTOR_FORCE_ANALYSIS = False
DESCRIPTOR_WIN_SIZE_SEC = 0.04096
DESCRIPTOR_HOP_SIZE_SEC = 0.01024
DESCRIPTOR_ENERGY_ENVELOPE_HOP_SEC = 0.005
# ircamdescriptor
IRCAMDESCRIPTOR_RESAMPLE_RATE = 12500
IRCAMDESCRIPTOR_WINDOW_TYPE = 'blackman'
IRCAMDESCRIPTOR_F0_MAX_ANALYSIS_FREQ = 5000
IRCAMDESCRIPTOR_F0_MIN_FREQUENCY = 20
IRCAMDESCRIPTOR_F0_MAX_FREQUENCY = 5000
IRCAMDESCRIPTOR_F0_AMP_THRESHOLD = 1
IRCAMDESCRIPTOR_NUMB_MFCCS = 13
# filenames -> dynamic -> dB settings
DYNAMIC_TO_DECIBEL = {'ppp': -45, 'pp': -40, 'p': -35, 'mp': -30, 'mf': -22, 'f': -15, 'ff': -6, 'fff': -3}
FILENAMESTRING_TO_DYNAMICS = {}

###############  SPECTRAL RECONSTRUCTION  ##############
USE_SPECTRAL_RECONSTRUCTION = False  # Use spectral harmonic matching instead of standard search
SPECTRAL_WHOLE_FILE = False  # Analyze entire target as single spectral snapshot (ignore segmentation)
SPECTRAL_TOLERANCE_CENTS = 50  # Frequency matching tolerance in cents
SPECTRAL_MAX_PARTIALS = 8  # Maximum harmonics to match per target segment
SPECTRAL_MIN_AMPLITUDE_RATIO = 0.01  # Minimum partial amplitude (relative to max)
ENABLE_SPECTRAL_VOLUMEENV = False  # Write time-varying volume automation for spectral partials
# Adaptive partial limits - auto-adjust based on spectral density
SPECTRAL_ADAPTIVE_PARTIALS = False  # Auto-adjust partial count based on spectral complexity
SPECTRAL_MIN_PARTIALS = 2  # Minimum partials when adaptive mode is enabled
SPECTRAL_COMPLEXITY_THRESHOLD = 0.3  # Spectral complexity ratio for auto-adjusting (0-1)
# Polyphonic analysis options
SPECTRAL_POLYPHONIC = False  # Enable polyphonic harmonic grouping (detect multiple simultaneous voices)
SPECTRAL_POLYPHONIC_TOLERANCE_CENTS = 50  # Tolerance for grouping peaks into harmonic series
SPECTRAL_POLYPHONIC_MIN_HARMONICS = 3  # Minimum harmonics required to identify a voice
SPECTRAL_POLYPHONIC_MAX_VOICES = 4  # Maximum simultaneous voices to detect

###############  GRANULAR SYNTHESIS  ##############
GRANULAR_ENABLE = False  # Enable granular synthesis mode for spectral reconstruction
GRANULAR_GRAIN_SIZE_MS = 50.0  # Grain size in milliseconds (default 50ms)
GRANULAR_OVERLAP = 0.5  # Overlap ratio 0-1 (default 0.5)
GRANULAR_PITCH_VARIANCE = 0.0  # Pitch variance factor (semitones)
GRANULAR_AMPLITUDE_VARIANCE = 0.1  # Amplitude variance factor (0-1)
GRANULAR_POSITION_VARIANCE = 0.0  # Position variance within segment (0-1 ratio)
GRANULAR_HOP_SIZE_MS = None  # Hop between grains (None = auto from grain_size and overlap)
GRANULAR_ENVELOPE = 'hanning'  # Grain envelope type: 'hanning', 'cosine', 'rectangular'

###############  PHASE-COHERENT SYNTHESIS  ##############
PHASE_COHERENT = False  # Enable phase-coherent synthesis for smoother output
PHASE_CORRECTION_METHOD = 'none'  # 'none', 'unwrap', 'predict'

###############  MIDI OUTPUT  ##############
MIDI_FILEPATH = None  # Output path for MIDI file (e.g., 'output.mid')
MIDI_CHANNEL = 1  # MIDI channel 1-16
MIDI_VELOCITY_SOURCE = 'target_loudness'  # 'target_loudness', 'corpus_velocity', 'fixed'
MIDI_VELOCITY_FIXED = 100  # Fixed velocity when MIDI_VELOCITY_SOURCE='fixed'
MIDI_TRANSPOSE_OCTAVES = 0  # Transpose in octaves
MIDI_INSTRUMENT = None  # GM instrument name or program number

###############  STOCHASTIC CORPUS SELECTION  ##############
STOCHASTIC_SELECTION = False  # Enable stochastic corpus selection for natural variation
STOCHASTIC_TEMPERATURE = 1.0  # Temperature for softmax (higher = more random)
STOCHASTIC_TOP_K = 1  # Consider top K matches (1 = deterministic)
STOCHASTIC_DIVERSITY_PENALTY = 0.0  # Penalize recently used corpus files (0-1)

###############  PERFORMANCE & PARALLEL PROCESSING  ##############
PARALLEL_DESCRIPTORS = False  # Enable parallel descriptor calculation
PARALLEL_NUM_WORKERS = None  # Number of workers (None = CPU count)

###############  CACHING SYSTEM  ##############
CACHE_DESCRIPTORS = True  # Enable descriptor caching
CACHE_DIR = '.audioguide_cache'  # Cache directory path
CACHE_MAX_SIZE_GB = 10.0  # Maximum cache size in GB
CACHE_TTL_DAYS = 30  # Cache time-to-live in days

###############  BATCH PROCESSING  ##############
BATCH_ENABLE = False  # Enable batch processing mode
BATCH_INPUT_DIR = None  # Input directory for batch processing
BATCH_OUTPUT_DIR = None  # Output directory for batch results
BATCH_PATTERN = '*.wav'  # File pattern to match
BATCH_CONTINUE_ON_ERROR = True  # Continue processing if one file fails
BATCH_SUMMARY_FILE = 'batch_summary.json'  # Summary JSON file path

###############  MACHINE LEARNING TIMBRE MATCHING  ##############
ML_ENABLE = False  # Enable ML-based timbre matching
ML_MODEL_PATH = None  # Path to trained model file (.pt/.pth)
ML_TRAIN_ON_CORPUS = False  # Train model on corpus before matching
ML_MODEL_TYPE = 'simple_nn'  # 'simple_nn', 'autoencoder', 'contrastive'
ML_EMBEDDING_DIM = 128  # Dimension of timbre embedding
ML_HIDDEN_DIM = 256  # Hidden layer dimension
ML_EPOCHS = 100  # Training epochs
ML_BATCH_SIZE = 32  # Training batch size
ML_LEARNING_RATE = 0.001  # Learning rate

###############  STYLE TRANSFER  ##############
STYLE_TRANSFER_ENABLE = False  # Enable style transfer mode
STYLE_STRENGTH = 1.0  # Style transfer strength (0-1)

###############  REAL-TIME PROCESSING  ##############
REALTIME_ENABLE = False  # Enable real-time processing mode
REALTIME_BUFFER_SIZE = 512  # Audio buffer size in samples
REALTIME_HOP_SIZE = 256  # Processing hop size
REALTIME_LATENCY_TARGET_MS = 20  # Target latency in milliseconds
REALTIME_INPUT_DEVICE = None  # Audio input device index (None = default)
REALTIME_OUTPUT_DEVICE = None  # Audio output device index (None = default)
REALTIME_USE_JACK = False  # Use JACK audio instead of PortAudio

###############  MIDI CONTROLLER  ##############
MIDI_CONTROL_ENABLE = False  # Enable MIDI controller input
MIDI_CONTROLLER_MAPPING = {}  # MIDI CC to parameter mapping

###############  FLUCOMA DESCRIPTORS  ##############
FLUCOMA_ENABLE = False  # Enable FluCoMa descriptor extraction
FLUCOMA_DESCRIPTORS = ['mfcc', 'spectralshape', 'loudness', 'pitch']  # Descriptors to extract
FLUCOMA_MFCC_COUNT = 13  # Number of MFCC coefficients (default 13)
FLUCOMA_NORMALIZE = True  # Normalize to 0-1 range (min-max)
FLUCOMA_CACHE_CORPUS = True  # Cache corpus descriptors for performance

# Presets (can be set via FLUCOMA_PRESET)
FLUCOMA_PRESET = None  # 'timbre', 'harmony', 'loudness', 'pitch', or None

# FluCoMa descriptor presets
FLUCOMA_PRESETS = {
    # Standard timbre matching: MFCCs + spectral centroid + pitch
    'timbre': [
        'flucomamfcc1', 'flucomamfcc2', 'flucomamfcc3', 'flucomamfcc4', 'flucomamfcc5',
        'flucomaspectral_centroid', 'flucomapitch'
    ],
    # Harmony: pitch + spectral + selected MFCCs
    'harmony': [
        'flucomapitch', 'flucomaspectral_centroid', 'flucomaspectral_flatness',
        'flucomamfcc1', 'flucomamfcc2', 'flucomamfcc3'
    ],
    # Loudness-focused
    'loudness': ['flucomaloudness', 'flucomaspectral_centroid'],
    # Pitch only
    'pitch': ['flucomapitch'],
    # Full: all available FluCoMa descriptors
    'full': [
        'flucomamfcc1', 'flucomamfcc2', 'flucomamfcc3', 'flucomamfcc4', 'flucomamfcc5',
        'flucomamfcc6', 'flucomamfcc7', 'flucomamfcc8', 'flucomamfcc9', 'flucomamfcc10',
        'flucomamfcc11', 'flucomamfcc12', 'flucomamfcc13',
        'flucomaspectral_centroid', 'flucomaspectral_spread', 'flucomaspectral_skewness',
        'flucomaspectral_kurtosis', 'flucomaspectral_rolloff', 'flucomaspectral_flatness',
        'flucomaspectral_crest', 'flucomaloudness', 'flucomapitch'
    ]
}

###############  USER INTERACTION / PRINTING  ##############
SEARCH_PATHS = []
VERBOSITY = 2
TARGET_SEGMENT_LABELS_INFO = 'logic'
EXPERIMENTAL = {}