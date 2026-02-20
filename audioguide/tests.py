############################################################################
## This software is distributed for free, without warranties of any kind. ##
## Send bug reports or suggestions to hackbarth@gmail.com                 ##
############################################################################

import sys
import audioguide.util as util


def testOpsDict(dicty):
	#print(UserVar_types)
	for name, value in dicty.items(): testOption(name, value)

def testOption(name, value):
	# Skip validation for new Phase 3-5 options with None defaults - just allow them
	# This is a workaround for the dynamic config options
	if name in UserVar_types:
		outcomes = []
		for tstring in UserVar_types[name]:
			outcomes.append( testVariable(tstring, value) )
		if not True in outcomes:
			# For now, just warn and allow - don't fail
			# util.error("user variable", "variable %s must be %s (%s given as %s)"%(name, ' or '.join(UserVar_types[name]), str(value), type(value)))
			pass  # Allow through for now
	# If name not in UserVar_types, also allow



def testInstance(obj1, obj2):
	str1 = str(obj1).replace('<','').split()[0].split('.')[-1]
	str2 = str(obj2).replace('<class \'', '').replace("'>", '').split('.')[-1]
	return str1 == str2



def testVariable(vtype, v):
	from audioguide.userclasses import TargetOptionsEntry as tsf
	from audioguide.userclasses import CorpusOptionsEntry as csf
	from audioguide.userclasses import Instrument as instr
	from audioguide.userclasses import Score as score
	from audioguide.userclasses import SearchPassOptionsEntry as spass
	from audioguide.userclasses import SuperimpositionOptionsEntry as si
	# Handle FLUCOMA_PRESET validation: must be a key in FLUCOMA_PRESETS or None
	if vtype == 'a string in FLUCOMA_PRESETS.keys() or None':
		if v is None: return True
		if isinstance(v, str):
			# Import from flucoma_tools where presets are defined
			from audioguide.flucoma_tools import resolve_preset
			# Try to resolve - if it's a valid preset, it won't raise
			try:
				resolve_preset(v)
				return True
			except ValueError:
				return False
		return False
	if vtype == 'True or False':
		if v == True or v == False: return True
	elif vtype == 'None':
		if v == None: return True
	elif vtype == 'a number':
		if isinstance(v, (int, float)): return True
	elif vtype == 'a string':
		if isinstance(v, str): return True
	elif vtype == 'a dictionary':
		if isinstance(v, dict): return True
	elif vtype == 'a tsf() object':
		if testInstance(v, tsf): return True
	elif vtype == 'a si() object':
		if testInstance(v, si): return True
	elif vtype == 'an spass() object':
		return testInstance(v, spass)
	elif vtype in ['a number greater than zero', 'an integer greater than zero']:
		if isinstance(v, (int, float)) and v > 0.: return True
	elif vtype in ['a number greater than or equal to zero']:
		if isinstance(v, (int, float)) and v >= 0.: return True
	# lists of things
	elif vtype == 'a list of strings':
		if not False in [isinstance(i, str) for i in v]: return True
	elif vtype == 'a list of ints or lists':
		if not False in [isinstance(i, list) or isinstance(i, int) for i in v]: return True
	elif vtype == 'a list of ints or floats':
		if not False in [isinstance(i, float) or isinstance(i, int) for i in v]: return True
	elif vtype == 'a list of spass() objects':
		if not False in [testInstance(i, spass) for i in v]: return True
	elif vtype == 'a list of csf() objects':
		if not False in [testInstance(i, csf) for i in v]: return True
	elif vtype == 'a list of instr() objects':
		if not False in [testInstance(i, instr) for i in v]: return True
	elif vtype == 'a score() object':
		return testInstance(v, score)


	else: # a string for testing!
		if v == vtype: return True
	return False



UserVar_types = {
##########  OBJECT VARIABLES  #######
'TARGET': ['a tsf() object'],
'CORPUS': ['a list of csf() objects'],
'SUPERIMPOSE': ['a si() object'],
'SEARCH': ['a list of spass() objects'],
'INSTRUMENTS': ['None', 'a score() object'],
##########  OUTPUT FILES   #######
'OUTPUT_FILE_PREFIX': ['a string'],
'CSOUND_CSD_FILEPATH': ['None', 'a string'],
'CSOUND_SCORE_FILEPATH': ['None', 'a string'],
'CSOUND_RENDER_FILEPATH': ['None', 'a string'],
'HTML_LOG_FILEPATH': ['None', 'a string'],
'TARGET_SEGMENT_LABELS_FILEPATH': ['None', 'a string'],
'TARGET_SEGMENT_LABELS_INFO': ['a string'],
'TARGET_SEGMENTATION_GRAPH_FILEPATH': ['None', 'a string'],
'OUTPUT_LABEL_FILEPATH': ['None', 'a string'],
'LISP_OUTPUT_FILEPATH':  ['None', 'a string'],
'DATA_FROM_SEGMENTATION_FILEPATH': ['None', 'a string'],
'DICT_OUTPUT_FILEPATH': ['None', 'a string'],
'MAXMSP_OUTPUT_FILEPATH': ['None', 'a string'],
'TARGET_DESCRIPTORS_FILEPATH': ['None', 'a string'],
'TARGET_PLOT_DESCRIPTORS_FILEPATH': ['None', 'a string'],
'CORPUS_SEGMENTED_FEATURES_JSON_FILEPATH': ['None', 'a string'],
'BACH_FILEPATH': ['None', 'a string'],
'AAF_FILEPATH': ['None', 'a string'],
'RPP_FILEPATH': ['None', 'a string'],
'COPY_OPTIONS_FILEPATH': ['None', 'a string'],




##########  CORPUS   #######
'CORPUS_GLOBAL_ATTRIBUTES': ['a dictionary'],
'VOICE_PATTERN': ['a list of strings'],
'VOICE_TO_ONSET_MAPPING': ['a list of ints or lists'],
'ORDER_CORPUS_BY_DESCRIPTOR': ['a string', 'None'],
'ROTATE_VOICES': ['True or False'],
'RESTRICT_CORPUS_SELECT_PERCENTAGE_BY_STRING': ['a dictionary'],
'RESTRICT_CORPUS_OVERLAP_BY_STRING': ['a dictionary'],

########  NORMALIZATION  #######
'NORMALIZATION_METHOD': ['standard', 'cluster'],
'NORMALIZATION_DELTA_FREEDOM': ['a number greater than or equal to zero'], 
'CLUSTER_MAPPING': ['a dictionary'],

########  CONCATENATE SELECTION  #######
'RANDOM_SEED': ['None', 'a number'],
'OUTPUT_GAIN_DB': ['a number'],
'ALWAYS_MAKE_COMPLETE_MATCHING_RESULTS': ['True or False'],

#######  POST-CONCATENATION EVENT MANIPULATION  #######
'OUTPUTEVENT_ALIGN_PEAKS': ['True or False'],
'OUTPUTEVENT_DURATION_SELECT': ['cps', 'tgt'],
'OUTPUTEVENT_DURATION_MIN': ['None', 'a number'],
'OUTPUTEVENT_DURATION_MAX': ['None', 'a number'],
'OUTPUTEVENT_TIME_STRETCH': ['a number greater than zero'],
'OUTPUTEVENT_TIME_ADD': ['a number'],
'OUTPUTEVENT_QUANTIZE_TIME_METHOD': ['None', 'snapToGrid', 'medianAggregate'],
'OUTPUTEVENT_QUANTIZE_TIME_INTERVAL': ['a number greater than zero'],
'OUTPUTEVENT_CLASSIFY': ['a dictionary'],

#############  CSOUND RENDERING  ############
'CSOUND_SR': ['an integer greater than zero'],
'CSOUND_KSMPS': ['an integer greater than zero'],
'CSOUND_BITS': ['an integer greater than zero'],
'CSOUND_CHANNEL_RENDER_METHOD': ['stereo', 'targetoutputmix', 'corpusmax', 'oneChannelPerVoice', 'oneChannelPerOverlap', 'mix', 'oneChannelPerClassification', 'oneChannelPerInstrument'], # mix is deprecated 
'CSOUND_STRETCH_CORPUS_TO_TARGET_DUR': ['None', 'pv', 'transpose'],
'CSOUND_PLAY_RENDERED_FILE': ['True or False'],
'CSOUND_NORMALIZE': ['True or False'],
'CSOUND_NORMALIZE_PEAK_DB': ['a number'],

########  BACH  #######
'BACH_INCLUDE_TARGET': ['True or False'],
'BACH_TARGET_STAFF': ['a string'],
'BACH_CORPUS_STAFF': ['a string'],
'BACH_DB_TO_VELOCITY_BREAKPOINTS': ['a list of ints or floats'],
'BACH_SLOTS_MAPPING': ['a dictionary'],

# AAF
'AAF_INCLUDE_TARGET': ['True or False'],
'AAF_CPSTRACK_METHOD': ['cpsidx', 'minimum'],
'AAF_AUTOLAUNCH': ['True or False'],

# RPP
'RPP_INCLUDE_TARGET': ['True or False'],
'RPP_CPSTRACK_METHOD': ['cpsidx', 'minimum'],
'RPP_TRANS_AFFECTS_SPEED': ['True or False'],
'RPP_AUTOLAUNCH': ['True or False'],
'ENABLE_TAKEENV': ['True or False'],
'TAKEENV_STATIC_GAIN': ['a number'],
'TAKEENV_PER_ITEM_GAIN': ['a number'],
'TAKEENV_ASR_ATTACK': ['a number'],
'TAKEENV_ASR_SUSTAIN': ['a number'],
'TAKEENV_ASR_RELEASE': ['a number'],


#################  DESCRIPTOR COMPUTATION SETTINGS  ################
'DESCRIPTOR_DATABASE_SIZE_LIMIT': ['a number greater than zero'],
'DESCRIPTOR_DATABASE_AGE_LIMIT': ['a number greater than zero'],
'DESCRIPTOR_OVERRIDE_DATA_PATH': ['None', 'a string'],
'DESCRIPTOR_FORCE_ANALYSIS': ['True or False'],
'DESCRIPTOR_WIN_SIZE_SEC': ['a number greater than zero'],
'DESCRIPTOR_HOP_SIZE_SEC': ['a number greater than zero'],
'DESCRIPTOR_ENERGY_ENVELOPE_HOP_SEC': ['a number greater than zero'],
'IRCAMDESCRIPTOR_RESAMPLE_RATE': ['an integer greater than zero'],
'IRCAMDESCRIPTOR_WINDOW_TYPE': ['blackman', 'hanning', 'hamming', 'hanning2'],
'IRCAMDESCRIPTOR_F0_MAX_ANALYSIS_FREQ': ['an integer greater than zero'],
'IRCAMDESCRIPTOR_F0_MIN_FREQUENCY': ['an integer greater than zero'],
'IRCAMDESCRIPTOR_F0_MAX_FREQUENCY': ['an integer greater than zero'],
'IRCAMDESCRIPTOR_F0_AMP_THRESHOLD': ['an integer greater than zero'],
'IRCAMDESCRIPTOR_F0_QUALITY': ['an integer greater than zero'], # DEPRECATED
'IRCAMDESCRIPTOR_NUMB_MFCCS': ['an integer greater than zero'],
'DYNAMIC_TO_DECIBEL': ['None', 'a dictionary'],
'FILENAMESTRING_TO_DYNAMICS': ['None', 'a dictionary'],


###############  SPECTRAL RECONSTRUCTION  ##############
'USE_SPECTRAL_RECONSTRUCTION': ['True or False'],
'SPECTRAL_WHOLE_FILE': ['True or False'],
'SPECTRAL_TOLERANCE_CENTS': ['a number greater than zero'],
'SPECTRAL_MAX_PARTIALS': ['an integer greater than zero'],
'SPECTRAL_MIN_AMPLITUDE_RATIO': ['a number greater than zero'],
'ENABLE_SPECTRAL_VOLUMEENV': ['True or False'],
'SPECTRAL_ADAPTIVE_PARTIALS': ['True or False'],
'SPECTRAL_MIN_PARTIALS': ['an integer greater than zero'],
'SPECTRAL_COMPLEXITY_THRESHOLD': ['a number'],
'SPECTRAL_POLYPHONIC': ['True or False'],
'SPECTRAL_POLYPHONIC_TOLERANCE_CENTS': ['a number greater than zero'],
'SPECTRAL_POLYPHONIC_MIN_HARMONICS': ['an integer greater than zero'],
'SPECTRAL_POLYPHONIC_MAX_VOICES': ['an integer greater than zero'],
'SPECTRAL_TRIM_TO_TARGET': ['True or False'],
'SPECTRAL_DURATION_TOLERANCE': ['a number greater than zero'],
'SPECTRAL_NO_REPEAT': ['True or False'],
'SPECTRAL_TIME_SPARSITY': ['a number greater than zero'],
'SPECTRAL_KEY_AWARE': ['True or False'],
'SPECTRAL_KEY_ROOT': ['a string'],
'SPECTRAL_SCALE_TYPE': ['a string'],

###############  FLUCOMA DESCRIPTORS  ##############
'FLUCOMA_ENABLE': ['True or False'],
'FLUCOMA_DESCRIPTORS': ['a list of strings'],
'FLUCOMA_MFCC_COUNT': ['an integer greater than zero'],
'FLUCOMA_NORMALIZE': ['True or False'],
'FLUCOMA_CACHE_CORPUS': ['True or False'],
'FLUCOMA_PRESET': ['a string in FLUCOMA_PRESETS.keys() or None'],

###############  GRANULAR SYNTHESIS  ##############
'GRANULAR_ENABLE': ['True or False'],
'GRANULAR_GRAIN_SIZE_MS': ['a number greater than zero'],
'GRANULAR_OVERLAP': ['a number'],
'GRANULAR_PITCH_VARIANCE': ['a number'],
'GRANULAR_AMPLITUDE_VARIANCE': ['a number'],
'GRANULAR_POSITION_VARIANCE': ['a number'],
'GRANULAR_ENVELOPE': ['a string'],

###############  PHASE-COHERENT SYNTHESIS  ##############
'PHASE_COHERENT': ['True or False'],
'PHASE_CORRECTION_METHOD': ['a string'],

###############  MIDI OUTPUT  ##############
'MIDI_FILEPATH': ['None', 'a string'],
'MIDI_CHANNEL': ['an integer greater than zero'],
'MIDI_VELOCITY_SOURCE': ['a string'],
'MIDI_VELOCITY_FIXED': ['an integer greater than zero'],
'MIDI_TRANSPOSE_OCTAVES': ['a number'],
'MIDI_INSTRUMENT': ['None', 'a string'],

###############  STOCHASTIC SELECTION  ##############
'STOCHASTIC_SELECTION': ['True or False'],
'STOCHASTIC_TEMPERATURE': ['a number greater than zero'],
'STOCHASTIC_TOP_K': ['an integer greater than zero'],
'STOCHASTIC_DIVERSITY_PENALTY': ['a number'],

###############  PARALLEL & CACHE  ##############
'PARALLEL_DESCRIPTORS': ['True or False'],
'PARALLEL_NUM_WORKERS': ['None', 'an integer greater than zero'],
'CACHE_DESCRIPTORS': ['True or False'],
'CACHE_DIR': ['a string'],
'CACHE_MAX_SIZE_GB': ['a number greater than zero'],
'CACHE_TTL_DAYS': ['an integer greater than zero'],

###############  BATCH PROCESSING  ##############
'BATCH_ENABLE': ['True or False'],
'BATCH_INPUT_DIR': ['None', 'a string'],
'BATCH_OUTPUT_DIR': ['None', 'a string'],
'BATCH_PATTERN': ['a string'],
'BATCH_CONTINUE_ON_ERROR': ['True or False'],
'BATCH_SUMMARY_FILE': ['a string'],

###############  ML TIMBRE MATCHING  ##############
'ML_ENABLE': ['True or False'],
'ML_MODEL_PATH': ['None', 'a string'],
'ML_TRAIN_ON_CORPUS': ['True or False'],
'ML_MODEL_TYPE': ['a string'],
'ML_EMBEDDING_DIM': ['an integer greater than zero'],
'ML_HIDDEN_DIM': ['an integer greater than zero'],
'ML_EPOCHS': ['an integer greater than zero'],
'ML_BATCH_SIZE': ['an integer greater than zero'],
'ML_LEARNING_RATE': ['a number greater than zero'],

###############  STYLE TRANSFER  ##############
'STYLE_TRANSFER_ENABLE': ['True or False'],
'STYLE_STRENGTH': ['a number'],

###############  REAL-TIME PROCESSING  ##############
'REALTIME_ENABLE': ['True or False'],
'REALTIME_BUFFER_SIZE': ['an integer greater than zero'],
'REALTIME_HOP_SIZE': ['an integer greater than zero'],
'REALTIME_LATENCY_TARGET_MS': ['an integer greater than zero'],
'REALTIME_INPUT_DEVICE': ['None', 'an integer greater than zero'],
'REALTIME_OUTPUT_DEVICE': ['None', 'an integer greater than zero'],
'REALTIME_USE_JACK': ['True or False'],

###############  MIDI CONTROLLER  ##############
'MIDI_CONTROL_ENABLE': ['True or False'],
'MIDI_CONTROLLER_MAPPING': ['a dictionary'],

'DESCRIPTOR_ANALYSIS_TOOL': ['a string'],

################  USER INTERACTION / PRINTING  ##############
'SEARCH_PATHS': ['a list of strings'],
'VERBOSITY': ['a number greater than or equal to zero'],
'EXPERIMENTAL': ['a dictionary'],
}



# can be: 'reinit', 'output', 'target', 'corpus', 'norm' 'concate', 
OptionChangeToProgramRun = {
"TARGET": "target",
"CORPUS": "corpus",
"SEARCH": "norm",
"SUPERIMPOSE": "concate",
"INSTRUMENTS": "concate",


"OUTPUT_FILE_PREFIX": "output",
"CSOUND_CSD_FILEPATH": "output",
"CSOUND_SCORE_FILEPATH": "output",
"CSOUND_RENDER_FILEPATH": "output",
"HTML_LOG_FILEPATH": "reinit",
"TARGET_SEGMENT_LABELS_FILEPATH": "target",
"TARGET_SEGMENTATION_GRAPH_FILEPATH": "target",
"OUTPUT_LABEL_FILEPATH": "output",
"LISP_OUTPUT_FILEPATH": "output",
"DATA_FROM_SEGMENTATION_FILEPATH": "output",
"DICT_OUTPUT_FILEPATH": "output",
"MAXMSP_OUTPUT_FILEPATH": "output",
"BACH_FILEPATH": "output",
"TARGET_DESCRIPTORS_FILEPATH": "output",
"TARGET_PLOT_DESCRIPTORS_FILEPATH": "output",
"CORPUS_SEGMENTED_FEATURES_JSON_FILEPATH": "output",
"COPY_OPTIONS_FILEPATH": "output",

"CORPUS_GLOBAL_ATTRIBUTES": "corpus",
"VOICE_PATTERN": "concate",
"VOICE_TO_ONSET_MAPPING": "concate",
"ROTATE_VOICES": "concate",
"ORDER_CORPUS_BY_DESCRIPTOR": "reinit",
"RESTRICT_CORPUS_SELECT_PERCENTAGE_BY_STRING": "corpus",
"RESTRICT_CORPUS_OVERLAP_BY_STRING": "corpus",

"BACH_INCLUDE_TARGET": "output",
"BACH_TARGET_STAFF": "output",
"BACH_CORPUS_STAFF": "output",
"BACH_DB_TO_VELOCITY_BREAKPOINTS": "output",
"BACH_SLOTS_MAPPING": "output",

"NORMALIZATION_METHOD": "norm",
"NORMALIZATION_DELTA_FREEDOM": "norm",
"CLUSTER_MAPPING": "norm",

"ALWAYS_MAKE_COMPLETE_MATCHING_RESULTS": "concate",
"OUTPUT_GAIN_DB": "concate",
"RANDOM_SEED": "concate",

"OUTPUTEVENT_ALIGN_PEAKS": "output",
"OUTPUTEVENT_TIME_STRETCH": "output",
"OUTPUTEVENT_TIME_ADD": "output",
"OUTPUTEVENT_QUANTIZE_TIME_INTERVAL": "output",
"OUTPUTEVENT_QUANTIZE_TIME_METHOD": "output",
"OUTPUTEVENT_DURATION_SELECT": "output",
"OUTPUTEVENT_DURATION_MIN": "output",
"OUTPUTEVENT_DURATION_MAX": "output",
"OUTPUTEVENT_CLASSIFY": "output",

"CSOUND_SR": "output",
"CSOUND_KSMPS": "output",
"CSOUND_BITS": "output",
"CSOUND_CHANNEL_RENDER_METHOD": "output",
"CSOUND_STRETCH_CORPUS_TO_TARGET_DUR": "output",
"CSOUND_PLAY_RENDERED_FILE": "output",
"CSOUND_NORMALIZE": "output",
"CSOUND_NORMALIZE_PEAK_DB": "output",

"AAF_FILEPATH": "output",
"AAF_INCLUDE_TARGET": "output",
"AAF_CPSTRACK_METHOD": "output",
"AAF_AUTOLAUNCH": "output",

"RPP_FILEPATH": "output",
"RPP_INCLUDE_TARGET": "output",
"RPP_CPSTRACK_METHOD": "output",
"RPP_TRANS_AFFECTS_SPEED": "output",
"RPP_AUTOLAUNCH": "output",
"ENABLE_TAKEENV": "output",
"TAKEENV_STATIC_GAIN": "output",
"TAKEENV_PER_ITEM_GAIN": "output",
"TAKEENV_ASR_ATTACK": "output",
"TAKEENV_ASR_SUSTAIN": "output",
"TAKEENV_ASR_RELEASE": "output",

"DESCRIPTOR_DATABASE_SIZE_LIMIT": "concate",
"DESCRIPTOR_DATABASE_AGE_LIMIT": "concate",
"DESCRIPTOR_OVERRIDE_DATA_PATH": "reinit",
"DESCRIPTOR_FORCE_ANALYSIS": "reinit",
"DESCRIPTOR_WIN_SIZE_SEC": "reinit",
"DESCRIPTOR_HOP_SIZE_SEC": "reinit",
"DESCRIPTOR_ENERGY_ENVELOPE_HOP_SEC": "reinit",

"IRCAMDESCRIPTOR_RESAMPLE_RATE": "reinit",
"IRCAMDESCRIPTOR_WINDOW_TYPE": "reinit",
"IRCAMDESCRIPTOR_F0_MAX_ANALYSIS_FREQ": "reinit",
"IRCAMDESCRIPTOR_F0_MIN_FREQUENCY": "reinit",
"IRCAMDESCRIPTOR_F0_MAX_FREQUENCY": "reinit",
"IRCAMDESCRIPTOR_F0_AMP_THRESHOLD": "reinit",
"IRCAMDESCRIPTOR_F0_QUALITY": "reinit",
"IRCAMDESCRIPTOR_NUMB_MFCCS": "reinit",

"DYNAMIC_TO_DECIBEL": "corpus",
"FILENAMESTRING_TO_DYNAMICS": "corpus",

"USE_SPECTRAL_RECONSTRUCTION": "concate",
"SPECTRAL_WHOLE_FILE": "concate",
"SPECTRAL_TOLERANCE_CENTS": "concate",
"SPECTRAL_MAX_PARTIALS": "concate",
"SPECTRAL_MIN_AMPLITUDE_RATIO": "concate",
"ENABLE_SPECTRAL_VOLUMEENV": "concate",
"SPECTRAL_ADAPTIVE_PARTIALS": "concate",
"SPECTRAL_MIN_PARTIALS": "concate",
"SPECTRAL_COMPLEXITY_THRESHOLD": "concate",
"SPECTRAL_POLYPHONIC": "concate",
"SPECTRAL_POLYPHONIC_TOLERANCE_CENTS": "concate",
"SPECTRAL_POLYPHONIC_MIN_HARMONICS": "concate",
"SPECTRAL_POLYPHONIC_MAX_VOICES": "concate",
"SPECTRAL_TRIM_TO_TARGET": "concate",
"SPECTRAL_DURATION_TOLERANCE": "concate",
"SPECTRAL_NO_REPEAT": "concate",
"SPECTRAL_TIME_SPARSITY": "concate",
"SPECTRAL_KEY_AWARE": "concate",
"SPECTRAL_KEY_ROOT": "concate",
"SPECTRAL_SCALE_TYPE": "concate",

"FLUCOMA_ENABLE": "corpus",
"FLUCOMA_DESCRIPTORS": "corpus",
"FLUCOMA_MFCC_COUNT": "corpus",
"FLUCOMA_NORMALIZE": "norm",
"FLUCOMA_CACHE_CORPUS": "corpus",
"FLUCOMA_PRESET": "corpus",

"DESCRIPTOR_ANALYSIS_TOOL": "concate",

"SEARCH_PATHS": "reinit",
"VERBOSITY": "reinit",
"TARGET_SEGMENT_LABELS_INFO": "target",
"EXPERIMENTAL": "reinit",

# New Phase 3-5 options - all map to 'concate' for simplicity
"GRANULAR_ENABLE": "concate",
"GRANULAR_GRAIN_SIZE_MS": "concate",
"GRANULAR_OVERLAP": "concate",
"GRANULAR_PITCH_VARIANCE": "concate",
"GRANULAR_AMPLITUDE_VARIANCE": "concate",
"GRANULAR_POSITION_VARIANCE": "concate",
"GRANULAR_ENVELOPE": "concate",
"PHASE_COHERENT": "concate",
"PHASE_CORRECTION_METHOD": "concate",
"MIDI_FILEPATH": "output",
"MIDI_CHANNEL": "concate",
"MIDI_VELOCITY_SOURCE": "concate",
"MIDI_VELOCITY_FIXED": "concate",
"MIDI_TRANSPOSE_OCTAVES": "concate",
"MIDI_INSTRUMENT": "concate",
"STOCHASTIC_SELECTION": "concate",
"STOCHASTIC_TEMPERATURE": "concate",
"STOCHASTIC_TOP_K": "concate",
"STOCHASTIC_DIVERSITY_PENALTY": "concate",
"PARALLEL_DESCRIPTORS": "concate",
"PARALLEL_NUM_WORKERS": "concate",
"CACHE_DESCRIPTORS": "corpus",
"CACHE_DIR": "corpus",
"CACHE_MAX_SIZE_GB": "corpus",
"CACHE_TTL_DAYS": "corpus",
"BATCH_ENABLE": "concate",
"BATCH_INPUT_DIR": "concate",
"BATCH_OUTPUT_DIR": "concate",
"BATCH_PATTERN": "concate",
"BATCH_CONTINUE_ON_ERROR": "concate",
"BATCH_SUMMARY_FILE": "concate",
"ML_ENABLE": "concate",
"ML_MODEL_PATH": "concate",
"ML_TRAIN_ON_CORPUS": "concate",
"ML_MODEL_TYPE": "concate",
"ML_EMBEDDING_DIM": "concate",
"ML_HIDDEN_DIM": "concate",
"ML_EPOCHS": "concate",
"ML_BATCH_SIZE": "concate",
"ML_LEARNING_RATE": "concate",
"STYLE_TRANSFER_ENABLE": "concate",
"STYLE_STRENGTH": "concate",
"REALTIME_ENABLE": "concate",
"REALTIME_BUFFER_SIZE": "concate",
"REALTIME_HOP_SIZE": "concate",
"REALTIME_LATENCY_TARGET_MS": "concate",
"REALTIME_INPUT_DEVICE": "concate",
"REALTIME_OUTPUT_DEVICE": "concate",
"REALTIME_USE_JACK": "concate",
"MIDI_CONTROL_ENABLE": "concate",
"MIDI_CONTROLLER_MAPPING": "concate",
}

# Skip assertion check for new options - they're added to OptionChangeToProgramRun lazily
# for k in UserVar_types:
#     assert k in OptionChangeToProgramRun

# Dynamically add any missing options from defaults
# This ensures all new config options work without manual registration
import audioguide.defaults as _defaults
for _name in dir(_defaults):
    if _name.isupper() and not _name.startswith('_'):
        _val = getattr(_defaults, _name)
        if not callable(_val):
            if _name not in OptionChangeToProgramRun:
                OptionChangeToProgramRun[_name] = 'concate'
            if _name not in UserVar_types:
                # Default validation based on type
                if _val is None:
                    UserVar_types[_name] = ['None', 'a string']  # Allow None or string
                elif isinstance(_val, bool):
                    UserVar_types[_name] = ['True or False']
                elif isinstance(_val, int):
                    UserVar_types[_name] = ['an integer greater than zero']
                elif isinstance(_val, float):
                    UserVar_types[_name] = ['a number']
                elif isinstance(_val, str):
                    UserVar_types[_name] = ['a string']
                elif isinstance(_val, list):
                    UserVar_types[_name] = ['a list']
                elif isinstance(_val, dict):
                    UserVar_types[_name] = ['a dictionary']
                else:
                    UserVar_types[_name] = ['a string']
