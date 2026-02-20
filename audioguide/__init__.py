############################################################################
## This software is distributed for free, without warranties of any kind. ##
## Send bug reports or suggestions to hackbarth@gmail.com                 ##
############################################################################

__author__ = "Benjamin Hackbarth, Norbert Schnell, Philippe Esling, Diemo Schwarz, Gilbert Nouno"
__author_email__ = "hackbarth@gmail.com"
__version__ = "1.79"




import sys, os, operator, platform, json
import numpy as np

import audioguide.util as util
import audioguide.sfsegment as sfsegment
import audioguide.userinterface as userinterface
import audioguide.concatenativeclasses as concatenativeclasses
import audioguide.anallinkage as anallinkage
import audioguide.descriptordata as descriptordata
import audioguide.fileoutput.musicalwriting as musicalwriting
import audioguide.simcalc as simcalc
import audioguide.tests as tests
import audioguide.dimscaling as dimscaling




class main:
	def __init__(self):
		self.ops = concatenativeclasses.parseOptionsV2()

	def set_option(self, optionname, optionvalue):
		self.ops.set_option(optionname, optionvalue)

	def parse_options_dict(self, opsdict, init=False):
		# if we are in interactive mode, this tests the new options to see
		# if any options disappeared that need to be repopulated with defaults.
		if not init and self.ops.interactive_mode_last_ops_dict != None:
			for k in self.ops.interactive_mode_last_ops_dict:
				if k not in opsdict:
					opsdict[k] = self.ops.defaultops[k]
		for optionname, optionvalue in opsdict.items():
			self.ops.set_option(optionname, optionvalue, init=init)
		# save it to inspect removed keys on next interactive pass
		self.ops.interactive_mode_last_ops_dict = opsdict 
		
	def parse_options_file(self, opspath, init=False):
		usrOptions = self.ops.parse_file(opspath)
		self.parse_options_dict(usrOptions, init=init)
		return os.path.getmtime(opspath)

	def execute(self, print_steps=False):
		'''execute runs all parts of the concatenative code depending on what options have changed'''
		initanal, target, corpus, norm, concate, output = self.ops.poll_options()
		files = {}
		if initanal:
			if print_steps: print("1. initializing analysis interface")
			self.initialize_analysis_interface()
		if target:
			if print_steps: print("2. loading target")
			self.load_target()
			self.write_target_output_files()
		if corpus:
			if print_steps: print("3. loading corpus")
			self.load_corpus()
		if norm:
			if print_steps: print("4. normalizing")
			self.normalize()
		if concate:
			if print_steps: print("5. concatenating")
			# Choose between standard and spectral reconstruction modes
			if self.ops.USE_SPECTRAL_RECONSTRUCTION:
				self.spectral_concatenate()
			else:
				self.standard_concatenate()
		if output:
			if print_steps: print("6. writing outputs")
			files = self.write_concatenate_output_files()
		self.ops.rewind() # clear list for future options changes
		return files
		

	def initialize_analysis_interface(self, printversion=True):
		if 'concateMethod' in self.ops.EXPERIMENTAL and self.ops.EXPERIMENTAL['concateMethod'] == 'framebyframe':
			util.error("CONFIG", "Frame by frame concatenation is only possible with the agConcatenateFrames.py script.")
		self.p = userinterface.printer(self.ops.VERBOSITY, os.path.dirname(__file__), self.ops.get_outputfile('HTML_LOG_FILEPATH'))
		if printversion: self.p.printProgramInfo(__version__)
		self.AnalInterface = self.ops.createAnalInterface(self.p)


	def load_target(self):
		self.p.logsection( "TARGET" )
		self.tgt = sfsegment.target(self.ops.TARGET, self.AnalInterface)
		self.tgt.initAnal(self.AnalInterface, self.ops, self.p)
		self.tgt.stageSegments(self.AnalInterface, self.ops, self.p)
		
		if len(self.tgt.segs) == 0:
			util.error("TARGET FILE", "no segments found!  this is rather strange.  could your target file %s be digital silence??"%(self.tgt.filename))
		self.p.log("TARGET SEGMENTATION: found %i segments with an average length of %.3f seconds"%(len(self.tgt.segs), np.average(self.tgt.seglengths)))

		descriptors = []
		dnames = []
		self.ops.parseDescriptors()
		for dobj in self.ops._normalizeDescriptors + self.ops._limitDescriptors:
			if dobj.seg or dobj.name in ['power']: continue
			d = np.array(self.tgt.whole.desc.get(dobj.name, copy=True))
			d -= np.min(d)
			d /= np.max(d)
			d = np.around(d, 2)
	
			descriptors.append(d)
			dnames.append(dobj.name)
		if self.p.html != None:
			self.p.html.jschart_timeseries(yarray=np.array([self.AnalInterface.f2s(i) for i in range(self.tgt.whole.lengthInFrames)]), xarrays=descriptors, ylabel='time in seconds', xlabels=dnames)

	def write_target_output_files(self):	
		#######################
		## target label file ##
		#######################
		if self.ops.TARGET_SEGMENT_LABELS_FILEPATH != None:
			self.tgt.writeSegmentationFile(self.ops.get_outputfile('TARGET_SEGMENT_LABELS_FILEPATH'))
			self.p.log( "TARGET: wrote segmentation label file %s"%self.ops.get_outputfile('TARGET_SEGMENT_LABELS_FILEPATH') )
		#############################
		## target descriptors file ##
		#############################
		if self.ops.TARGET_DESCRIPTORS_FILEPATH != None:
			self.tgt.whole.desc.writedict(self.ops.get_outputfile('TARGET_DESCRIPTORS_FILEPATH'), ag.AnalInterface)
			self.p.log("TARGET: wrote descriptors to %s"%(self.ops.get_outputfile('TARGET_DESCRIPTORS_FILEPATH')))
		##############################
		## target descriptor graphs ##
		##############################
		if self.ops.TARGET_PLOT_DESCRIPTORS_FILEPATH != None:
			self.tgt.plotMetrics(self.ops.get_outputfile('TARGET_PLOT_DESCRIPTORS_FILEPATH'), self.AnalInterface, self.p)
		###############################
		## target segmentation graph ##
		###############################
		if self.ops.TARGET_SEGMENTATION_GRAPH_FILEPATH != None:
			self.tgt.plotSegmentation(self.ops.get_outputfile('TARGET_SEGMENTATION_GRAPH_FILEPATH'), self.AnalInterface, self.p)




	def load_corpus(self):
		############
		## CORPUS ##
		############
		self.p.logsection( "CORPUS" )
		self.cps = concatenativeclasses.corpus(self.ops.CORPUS, self.ops.CORPUS_GLOBAL_ATTRIBUTES, self.ops.RESTRICT_CORPUS_SELECT_PERCENTAGE_BY_STRING, self.ops.SEARCH_PATHS, self.AnalInterface, self.p)

		htmlCorpusTable = [['', 'minimum', 'maximum', 'average']]
		segmentLength = [c.segmentDurationSec for c in self.cps.postLimitSegmentNormList]
		htmlCorpusTable.append(['segment length', min(segmentLength), max(segmentLength), np.mean(segmentLength)])
		power = [c.desc.get('power-seg') for c in self.cps.postLimitSegmentNormList]
		htmlCorpusTable.append(['power', np.min(power), np.max(power), np.mean(power)])
		self.p.maketable(htmlCorpusTable, resolution=5)




	def dimensional_scale_data(self):
		self.ops.parseDescriptors()
		dimscaling.buildarray_all_timevarying_descriptors(self.tgt.segs + self.cps.postLimitSegmentNormList, self.ops._normalizeDescriptors, self.AnalInterface)
		from userclasses import SearchPassOptionsEntry as spass
		from userclasses import SingleDescriptor as d
		self.ops.SEARCH = [
spass('closest_percent', d('effDur-seg', norm=1), d('power-seg', norm=1), percent=25),
spass('closest', d('X', norm=1), d('Y', norm=1))
]



	def normalize(self):
		###################
		## NORMALIZATION ##
		###################
		self.p.logsection( "NORMALIZATION" )
		self.ops.parseDescriptors()
		self.AnalInterface.desc_manager.normalize(self.tgt.segs + self.cps.postLimitSegmentNormList, self.ops._normalizeDescriptors)
		###########################################################################
		## get raw and normalized segemented desciptors for graphing in log.html ##
		###########################################################################
		self.p.makeHtmlChartDescriptorNorm(self.ops._normalizeDescriptors+self.ops._limitDescriptors, self.ops._normalizeDescriptors, self.tgt.segs, self.cps.postLimitSegmentNormList)	
		
	
		
	
	
	def standard_concatenate(self):
		##############################
		## initialise concatenation ##
		##############################
		self.p.logsection( "CONCATENATION" )
		self.tgt.setupConcate(self.ops._mixtureDescriptors)
		self.AnalInterface.done(dataGbLimit=self.ops.DESCRIPTOR_DATABASE_SIZE_LIMIT, dataDayLimit=self.ops.DESCRIPTOR_DATABASE_AGE_LIMIT)
		distanceCalculations = simcalc.distanceCalculations(self.ops.SUPERIMPOSE, self.ops.RANDOM_SEED, self.AnalInterface, self.tgt.segs, self.p)
		distanceCalculations.setTarget(self.ops.SEARCH, self.tgt.segs)

		self.instruments = musicalwriting.instruments(self.ops.INSTRUMENTS, self.ops.CORPUS, self.tgt.segs, self.tgt.lengthInFrames, self.cps.postLimitSegmentNormList, self.AnalInterface.hopLengthSec, self.p)

		superimp = concatenativeclasses.SuperimposeTracker(self.tgt.lengthInFrames, len(self.tgt.segs), self.ops.SUPERIMPOSE.overlapAmpThresh, self.ops.SUPERIMPOSE.peakAlign, self.ops.SUPERIMPOSE.peakAlignEnvelope, len(self.ops.CORPUS), self.ops.RESTRICT_CORPUS_OVERLAP_BY_STRING, self.p)
		superimp.setup_subtract(self.ops.SUPERIMPOSE.subtractScale, self.tgt.segs, self.cps.postLimitSegmentNormList)

		self.cps.setupConcate(self.tgt, self.AnalInterface)
		self.outputEvents = []

		#######################################
		### sort segments by power if needed ##
		#######################################
		if self.ops.SUPERIMPOSE.searchOrder == 'power':
			self.tgt.segs = sorted(self.tgt.segs, key=operator.attrgetter("power"), reverse=True)
		else:
			self.tgt.segs = sorted(self.tgt.segs, key=operator.attrgetter("segmentStartSec"))

		#################
		## CONCATENATE ##
		#################
		self.p.startPercentageBar(upperLabel="CONCATINATING", total=len(self.tgt.segs)+1)
		htmlSelectionTable = [['time x overlap', ]]
		for sidx, s in enumerate(self.ops.SEARCH):
			htmlSelectionTable[0].append('spass #%s: %s'%(sidx+1, s.method))
		while False in [t.selectiondone for t in self.tgt.segs]:
			self.p.percentageBarNext()
			for segidx, tgtseg in enumerate(self.tgt.segs):
				if tgtseg.selectiondone == True:
					continue
				##############################################################
				## check to see if we are done with this particular segment ##
				##############################################################
				if tgtseg.seek >= tgtseg.lengthInFrames: 
					tgtseg.selectiondone = True
					continue 
				########################################
				## run selection superimposition test ##
				########################################
				tif = tgtseg.segmentStartFrame+tgtseg.seek
				if tif >= self.tgt.lengthInFrames:
					tgtseg.selectiondone = True
					continue 
				timeInSec = self.AnalInterface.f2s(tif)
				tgtsegdur =  tgtseg.segmentDurationSec - self.AnalInterface.f2s(tgtseg.seek)
				segidxt = superimp.test('segidx', segidx, self.ops.SUPERIMPOSE.minSegment, self.ops.SUPERIMPOSE.maxSegment)
				overt = superimp.test('overlap', tif, self.ops.SUPERIMPOSE.minOverlap, self.ops.SUPERIMPOSE.maxOverlap)
				onsett = superimp.test('onset', tif, self.ops.SUPERIMPOSE.minFrame, self.ops.SUPERIMPOSE.maxFrame)
				trigVal = tgtseg.thresholdTest(tgtseg.seek, self.AnalInterface.tgtOnsetDescriptors)
				trig = trigVal >= self.tgt.segmentationThresh
				####################################################
				# skip selecting if some criteria doesn't match!!! #
				####################################################
				if 'notok' in [onsett, overt, segidxt]:
					if segidxt == 'notok':
						superimp.skip('maximum selections this segment', superimp.cnt['segidx'][segidx], timeInSec)
					if onsett == 'notok':
						superimp.skip('maximum onsets at this time', superimp.cnt['onset'][tif], timeInSec)
					if overt == 'notok':
						superimp.skip('maximum overlapping selections', superimp.cnt['overlap'][tif], timeInSec)
					tgtseg.seek += self.ops.SUPERIMPOSE.incr
					continue # next frame
				##############################################################
				## see if a selection should be forced without thresholding ##
				##############################################################
				if 'force' not in [onsett, overt, segidxt]: # test for amplitude threshold
					if not trig:
						superimp.skip('target too soft', trigVal, timeInSec)
						tgtseg.seek += self.ops.SUPERIMPOSE.incr
						continue # not loud enough, next frame
				##############################
				## get valid corpus handles ##
				##############################
				validSegments = self.cps.evaluateValidSamples(tif, timeInSec, tgtseg.idx, self.ops.ROTATE_VOICES, self.ops.VOICE_PATTERN, self.ops.VOICE_TO_ONSET_MAPPING, self.ops.CLUSTER_MAPPING, tgtseg.classification, superimp, self.instruments)
				if len(validSegments) == 0:
					superimp.skip('no corpus sounds made it past restrictions and limitations', None, timeInSec)
					tgtseg.seek += self.ops.SUPERIMPOSE.incr
					continue		
				distanceCalculations.setCorpus(validSegments)
				################################################
				## search and see if we find a winning sample ##
				################################################
				returnBool = distanceCalculations.executeSearch(tgtseg, tgtseg.seek, self.ops.SEARCH, self.ops.SUPERIMPOSE)
				if not returnBool: # nothing valid, so skip to new frame...
					superimp.skip('no corpus sounds made it through the search passes', None, timeInSec)
					tgtseg.seek += self.ops.SUPERIMPOSE.incr
					maxoverlaps = np.max(superimp.cnt['overlap'][tgtseg.seek:tgtseg.seek+tgtseg.lengthInFrames])
					htmlSelectionTable.append(["%.2fx%i"%(timeInSec, int(maxoverlaps)+1), ] + distanceCalculations.lengthAtPassesVerbose )
					continue
				###################################################
				## if passing this point, picking a corpus sound ##
				###################################################
				superimp.pick(trig, trigVal, onsett, overt, segidxt, timeInSec)
				selectCpsseg = distanceCalculations.returnSearch()
				#####################################
				## MODIFY CHOSEN SAMPLES AMPLITUDE ##
				#####################################
				minLen = min(tgtseg.lengthInFrames-tgtseg.seek, selectCpsseg.lengthInFrames)	
				# apply amp scaling
				sourceAmpScale = util.dbToAmp(self.ops.OUTPUT_GAIN_DB)
				sourceAmpScale *= util.dbToAmp(selectCpsseg.envDb)
				###################$###########################
				## subtract power and update onset detection ##
				###################$###########################
				if self.ops.SUPERIMPOSE.calcMethod != None:
					tgtseg.desc.mixture_subtract(selectCpsseg, sourceAmpScale*superimp.subtract_scalar, minLen, verbose=True)
				#####################################
				## mix chosen sample's descriptors ##
				#####################################
				if self.ops.SUPERIMPOSE.calcMethod == "mixture":
					tgtseg.desc.mixture_mix(selectCpsseg, sourceAmpScale, tgtseg.seek, self.ops._mixtureDescriptors)
					tgtseg.has_been_mixed = True
				#################################
				## append selected corpus unit ##
				#################################
				transposition = util.getTransposition(tgtseg, selectCpsseg)
				self.cps.updateWithSelection(selectCpsseg, timeInSec, segidx)
				cpsEffDur = selectCpsseg.desc.get('effDurFrames-seg')
				maxoverlaps = np.max(superimp.cnt['overlap'][tif:tif+minLen])
				eventTime = (timeInSec*self.ops.OUTPUTEVENT_TIME_STRETCH)+self.ops.OUTPUTEVENT_TIME_ADD

				transposition, sourceAmpScale = self.tgt.partial_analysis_cpsseg_winner(selectCpsseg, transposition, sourceAmpScale)

				oeObj = concatenativeclasses.outputEvent(selectCpsseg, eventTime, util.ampToDb(sourceAmpScale), transposition, superimp.cnt['selectionCount'], tgtseg, maxoverlaps, tgtsegdur, tgtseg.idx, self.ops.CSOUND_STRETCH_CORPUS_TO_TARGET_DUR, self.AnalInterface.f2s(1), self.ops.OUTPUTEVENT_DURATION_SELECT, self.ops.OUTPUTEVENT_DURATION_MIN, self.ops.OUTPUTEVENT_DURATION_MAX, self.ops.OUTPUTEVENT_ALIGN_PEAKS)
				self.outputEvents.append( oeObj )
		
				corpusname = os.path.split(self.cps.data['vcToCorpusName'][selectCpsseg.voiceID])[1]
				superimp.increment(tif, tgtseg.desc.get('effDurFrames-seg', start=tgtseg.seek), segidx, selectCpsseg, distanceCalculations.returnSearchPassText(), corpusname)

				self.instruments.increment(tif, tgtseg.desc.get('effDurFrames-seg', start=tgtseg.seek), oeObj)

				tgtseg.numberSelectedUnits += 1

				printLabel = "searching @ %.2f x %i"%(timeInSec, maxoverlaps+1)
				printLabel += ' '*(24-len(printLabel))
				printLabel += "search pass lengths: %s"%('  '.join(distanceCalculations.lengthAtPasses))
				self.p.percentageBarNext(lowerLabel=printLabel, incr=0)
				htmlSelectionTable.append(["%.2fx%i"%(timeInSec, int(maxoverlaps)+1), ] + distanceCalculations.lengthAtPassesVerbose )

		self.p.percentageBarClose(txt='Selected %i events'%len(self.outputEvents))
		self.p.maketable(htmlSelectionTable)



	def spectral_concatenate(self):
		"""
		Spectral reconstruction concatenation mode.

		Instead of standard descriptor matching, this mode:
		1. Extracts harmonic series from each target segment
		2. Matches corpus sounds to individual harmonics by frequency
		3. Layers corpus sounds with appropriate gain to recreate target spectrum
		"""
		import audioguide.spectrallayering as spectrallayering

		##############################
		## Initialize ##
		##############################
		self.p.logsection( "SPECTRAL RECONSTRUCTION" )
		self.tgt.setupConcate(self.ops._mixtureDescriptors)
		self.AnalInterface.done(dataGbLimit=self.ops.DESCRIPTOR_DATABASE_SIZE_LIMIT, dataDayLimit=self.ops.DESCRIPTOR_DATABASE_AGE_LIMIT)

		self.cps.setupConcate(self.tgt, self.AnalInterface)

		# Initialize instruments for output file generation
		self.instruments = musicalwriting.instruments(self.ops.INSTRUMENTS, self.ops.CORPUS, self.tgt.segs, self.tgt.lengthInFrames, self.cps.postLimitSegmentNormList, self.AnalInterface.hopLengthSec, self.p)
		self.outputEvents = []

		# Get all corpus segments
		# postLimitSegmentNormList is a list of corpusSegment objects
		all_corpus_segments = self.cps.postLimitSegmentNormList

		# Optionally compute f0 using pluggable descriptor backends
		backend_name = getattr(self.ops, 'DESCRIPTOR_ANALYSIS_TOOL', None)
		if backend_name and backend_name.lower() != 'default':
			self.p.log("Using %s backend for corpus f0 analysis...\n" % backend_name)
			analyzed_count = spectrallayering.compute_corpus_spectral_f0(
				all_corpus_segments,
				backend_name=backend_name,
				verbose=(self.ops.VERBOSITY >= 1)
			)
			self.p.log("  Analyzed %d corpus files with %s backend\n" % (analyzed_count, backend_name))

		##############################
		## Determine target segments to process ##
		##############################
		# If SPECTRAL_WHOLE_FILE is enabled, process entire target as single segment
		if self.ops.SPECTRAL_WHOLE_FILE:
			# Use the 'whole' sfsegment which covers the entire target file
			target_segments = [self.tgt.whole]
			self.p.log("Spectral whole-file mode: analyzing entire target as single spectral snapshot\n")
		else:
			# Use normal segmentation
			target_segments = self.tgt.segs

		self.p.log("Spectral reconstruction mode: matching %d target segments to %d corpus segments\n" %
			      (len(target_segments), len(all_corpus_segments)))

		# Track corpus file usage for no-repeat and time sparsity features
		# Key: corpus segment filename, Value: last usage time (in target timeline seconds)
		corpus_usage_tracker = {}

		# Key-aware filtering settings (extracted once before loop)
		key_aware = getattr(self.ops, 'SPECTRAL_KEY_AWARE', False)
		key_root = getattr(self.ops, 'SPECTRAL_KEY_ROOT', 'C')
		scale_type = getattr(self.ops, 'SPECTRAL_SCALE_TYPE', 'major')

		# Auto-detect key if requested
		if key_aware and key_root.lower() == 'auto':
			self.p.log("Auto-detecting musical key from target audio...\n")
			# Collect all frequencies from all target segments for key detection
			all_freqs = []
			all_amps = []
			for seg in target_segments:
				# Load and extract segment audio
				import soundfile as sf
				audio_data, sr = sf.read(seg.filename)
				if len(audio_data.shape) > 1:
					audio_data = audio_data.mean(axis=1)
				start_sample = int(seg.segmentStartSec * sr)
				end_sample = int((seg.segmentStartSec + seg.segmentDurationSec) * sr)
				target_audio = audio_data[start_sample:end_sample]

				# Analyze spectral content
				if getattr(self.ops, 'SPECTRAL_POLYPHONIC', False):
					# Polyphonic mode: extract all peaks and group into voices
					all_peaks = spectralanalysis.extract_all_spectral_peaks(
						target_audio, sr, fmin=80, fmax=2000,
						min_amplitude_ratio=self.ops.SPECTRAL_MIN_AMPLITUDE_RATIO,
						max_peaks=32
					)
					if len(all_peaks) > 0:
						voices = spectralanalysis.group_peaks_into_harmonic_series(
							all_peaks,
							tolerance_cents=getattr(self.ops, 'SPECTRAL_POLYPHONIC_TOLERANCE_CENTS', 50),
							min_harmonics=getattr(self.ops, 'SPECTRAL_POLYPHONIC_MIN_HARMONICS', 3),
							max_voices=getattr(self.ops, 'SPECTRAL_POLYPHONIC_MAX_VOICES', 4)
						)
						# Collect f0 from each voice
						for voice in voices:
							all_freqs.append(voice['f0'])
							all_amps.append(voice['strength'])
				else:
					# Monophonic mode: analyze single spectrum
					spectrum = spectralanalysis.analyze_segment_spectrum(
						target_audio, sr, fmin=80, fmax=2000, n_harmonics=16
					)
					if spectrum['f0'] > 0:
						all_freqs.append(spectrum['f0'])
						# Use max harmonic amplitude as weight
						all_amps.append(max(h[1] for h in spectrum['harmonics']) if spectrum['harmonics'] else 1.0)

			# Detect key
			detected_root, detected_scale = spectrallayering.detect_key_from_frequencies(all_freqs, all_amps)
			key_root = detected_root
			scale_type = detected_scale
			self.p.log("  Detected key: %s %s\n" % (key_root, scale_type))

		##############################
		## Process each target segment ##
		##############################
		for target_idx, target_seg in enumerate(target_segments):
			# Run spectral matching
			# Duration tolerance: only use when NOT trimming (prevents mismatched durations)
			duration_tolerance = None
			if not getattr(self.ops, 'SPECTRAL_TRIM_TO_TARGET', False):
				duration_tolerance = getattr(self.ops, 'SPECTRAL_DURATION_TOLERANCE', None)

			# No-repeat and time sparsity settings
			no_repeat = getattr(self.ops, 'SPECTRAL_NO_REPEAT', False)
			time_sparsity = getattr(self.ops, 'SPECTRAL_TIME_SPARSITY', None)

			spectral_matches = spectrallayering.spectral_layering_match(
				target_seg,
				all_corpus_segments,
				self.AnalInterface,
				tolerance_cents=self.ops.SPECTRAL_TOLERANCE_CENTS,
				max_partials=self.ops.SPECTRAL_MAX_PARTIALS,
				min_amplitude_ratio=self.ops.SPECTRAL_MIN_AMPLITUDE_RATIO,
				enable_polyphonic=getattr(self.ops, 'SPECTRAL_POLYPHONIC', False),
				polyphonic_tolerance_cents=getattr(self.ops, 'SPECTRAL_POLYPHONIC_TOLERANCE_CENTS', 50),
				polyphonic_min_harmonics=getattr(self.ops, 'SPECTRAL_POLYPHONIC_MIN_HARMONICS', 3),
				polyphonic_max_voices=getattr(self.ops, 'SPECTRAL_POLYPHONIC_MAX_VOICES', 4),
				duration_tolerance_sec=duration_tolerance,
				corpus_usage_tracker=corpus_usage_tracker,
				no_repeat=no_repeat,
				time_sparsity_sec=time_sparsity,
				current_time_sec=target_seg.segmentStartSec,
				key_aware=key_aware,
				key_root=key_root,
				scale_type=scale_type
			)


			# NORMALIZE GAINS for this target segment to prevent clipping
			# spectral_matches is already for just this target segment
			if len(spectral_matches) > 0:
				max_gain_db = max(m['gain_db'] for m in spectral_matches)
				if max_gain_db > 0:
					# Scale all gains down so max becomes 0dB
					gain_reduction = -max_gain_db
					for match in spectral_matches:
						match['gain_db'] += gain_reduction
						# Also update gain_envelope if present
						if 'gain_envelope' in match and match['gain_envelope'] is not None:
							match['gain_envelope'] = [(t, amp_db + gain_reduction)
													for t, amp_db in match['gain_envelope']]

			# Convert to AudioGuide output events - create event structure with all required attributes
			for match in spectral_matches:
				corpus_seg = match['corpus_segment']

				# Create event object
				class SpectralEvent:
					def makeDictOutput(self):
						dicty = {}
						for key in ['timeInScore', 'sfchnls', 'duration', 'envAttackSec', 'envDecaySec', 'envSlope', 'filename', 'peaktimeSec', 'sfSkip', 'transposition', 'tgtsegnumb', 'envDb']:
							dicty[key] = getattr(self, key)
						dicty['corpusIdNumber'] = self.voiceID
						dicty['classificationNumber'] = self.classification
						dicty['simultaneousSelectionNumber'] = self.simSelects
						dicty['peakRms'] = self.powerSeg
						dicty['peakRmsDb'] = self.rmsSeg
						dicty['midiPitch'] = self.midi
						dicty['envScaleDb'] = self.envDb
						return dicty
					def makeMaxMspListOutput(self):
						# time values in milliseconds!
						return [round(self.timeInScore*1000., 1), round(self.duration*1000., 1), self.filename, round(self.sfSkip*1000., 1), self.envDb, self.transposition, round(self.envAttackSec*1000., 1), round(self.envDecaySec*1000., 1)]

					def makeLabelText(self):
						if self.metadata != '':
							text=self.metadata
						elif self.sfSkip == 0:
							text = "%s"%(self.printName)
						else:
							text = "%s@%.2f"%(self.printName, self.sfSkip)
						return "%f\t%f\t%s\n"%(self.timeInScore, self.timeInScore+self.duration, text)

					def makeLispText(self):
						return '(%.3f %.3f %.3f "%s" %.2f) '%(self.timeInScore, self.duration, self.midi, self.filename, self.rmsSeg)

					def makeCsoundOutputText(self, channelMethod, instru=1):
						if channelMethod == 'mix': channelMethod = 'stereo'
						return "i%i  %.3f  %.3f  %.3f  \"%s\"  %.3f  %.3f  %.3f  %.3f  %.3f  %.3f  %.3f  %.3f  %.3f  %i  %i  %f  %i  %i  \"%s\"  \"%s\"\n"%(instru, self.timeInScore, self.duration, self.envDb, self.filename, self.sfSkip, self.transposition, self.rmsSeg, self.peaktimeSec, self.effDurSec, self.envAttackSec, self.envDecaySec, self.envSlope, self.voiceID, self.selectedInstrumentIdx, self.simSelects, self.tgtsegdur, self.tgtsegnumb, self.classification, self.stretchcode, channelMethod)


					
					pass

				output_event = SpectralEvent()

				# Corpus segment attributes
				output_event.sfseghandle = corpus_seg
				output_event.filename = corpus_seg.filename
				output_event.printName = corpus_seg.printName if hasattr(corpus_seg, 'printName') else corpus_seg.filename
				output_event.sfSkip = corpus_seg.segmentStartSec
				output_event.cpsduration = corpus_seg.segmentDurationSec
				output_event.voiceID = corpus_seg.voiceID if hasattr(corpus_seg, 'voiceID') else 0
				output_event.sfchnls = corpus_seg.soundfileChns if hasattr(corpus_seg, 'soundfileChns') else 1

				# Audio properties
				output_event.powerSeg = corpus_seg.desc.get('power-seg') if hasattr(corpus_seg, 'desc') else 1.0
				output_event.rmsSeg = 20.0 * np.log10(output_event.powerSeg) if output_event.powerSeg > 0 else -120.0
				output_event.effDurSec = corpus_seg.desc.get('effDur-seg') if hasattr(corpus_seg, 'desc') else corpus_seg.segmentDurationSec
				output_event.peaktimeSec = corpus_seg.desc.get('peakTime-seg') * self.AnalInterface.f2s(1) if hasattr(corpus_seg, 'desc') else 0.0

				# MIDI pitch (from spectral matching, NO transposition)
				target_freq = match['target_partial_freq']
				output_event.midi = 69 + 12 * np.log2(target_freq / 440.0) if target_freq > 0 else 60
				output_event.midiVelocity = min(127, max(10, int(output_event.rmsSeg + 127)))

				# Timing and duration
				output_event.timeInScore = target_seg.segmentStartSec

				# Duration: match target segment if SPECTRAL_TRIM_TO_TARGET enabled, else use corpus duration
				if getattr(self.ops, 'SPECTRAL_TRIM_TO_TARGET', False):
					output_event.duration = target_seg.segmentDurationSec
				else:
					output_event.duration = corpus_seg.segmentDurationSec

				output_event.tgtsegdur = target_seg.segmentDurationSec
				output_event.tgtsegnumb = target_idx

				# Transposition (NONE for spectral reconstruction)
				output_event.transposition = 0.0
				output_event.transratio = 1.0
				output_event.transposeSpeedChange = 1.0

				# Amplitude and envelope
				output_event.envDb = match['gain_db']

				# Add quick fade-out if trimming to prevent clicks
				if getattr(self.ops, 'SPECTRAL_TRIM_TO_TARGET', False):
					# Short fade-out at end (10ms) to prevent click when trimming long corpus sounds
					fade_out_time = min(0.01, target_seg.segmentDurationSec * 0.1)  # 10ms or 10% of duration
					output_event.envDecaySec = fade_out_time
				else:
					output_event.envDecaySec = 0.005  # Default short release
				output_event.ampRatio = 10 ** (match['gain_db'] / 20.0)
				output_event.envAttackSec = 0.01
				output_event.envSlope = 1.0

				# Additional required attributes
				output_event.simSelects = 0
				output_event.selectedInstrumentIdx = 0
				output_event.classification = 0
				output_event.stretchcode = ''
				output_event.dynamicFromFilename = ''
				output_event.metadata = ''
				output_event.instrTag = None
				output_event.instrParams = None
				output_event.extraDataFromSegmentationFile = ''
				output_event.selection_cnt = 0

				# Store gain envelope for RPP output
				output_event.gain_envelope = match['gain_envelope']

				self.outputEvents.append(output_event)

			# Progress logging
			if (target_idx + 1) % 10 == 0:
				self.p.log("  Processed %d/%d target segments\n" % (target_idx + 1, len(self.tgt.segs)))

		self.p.log("Generated %d output events from spectral matching\n" % len(self.outputEvents))


	def write_concatenate_output_files(self):
		dict_of_files_written = {}
		##########################################
		## sort self.outputEvents by start time ##
		##########################################
		self.outputEvents.sort(key=lambda x: x.timeInScore)
		eventsBool = len(self.outputEvents) > 0

		###########################
		## temporal quantization ##
		###########################
		concatenativeclasses.quantizeTime(self.outputEvents, self.ops.OUTPUTEVENT_QUANTIZE_TIME_METHOD, float(self.ops.OUTPUTEVENT_QUANTIZE_TIME_INTERVAL), self.p)


		##################################
		## CORPUS OUTPUT CLASSIFICATION ##
		##################################
		if eventsBool and self.ops.OUTPUTEVENT_CLASSIFY['numberClasses'] > 1:
			classifications = descriptordata.soundSegmentClassification(self.ops.OUTPUTEVENT_CLASSIFY['descriptors'], [oe.sfseghandle for oe in self.outputEvents], numbClasses=self.ops.OUTPUTEVENT_CLASSIFY['numberClasses'])
			for cidx, classified in enumerate(classifications): self.outputEvents[cidx].classification = int(classified)	


		#########################################
		## target signal decomposition cleanup ##
		#########################################
		if self.tgt.decompose != {}:
			for oeidx, oe in enumerate(self.outputEvents): 
				self.outputEvents[oeidx].decomposedstream = int(oe.timeInScore/self.tgt.decompose['origduration'])
				oe.timeInScore = oe.timeInScore%self.tgt.decompose['origduration']
			self.tgt.filename = self.tgt.decompose['origfilename']
			self.tgt.startSec = 0
			self.tgt.endSec = self.tgt.decompose['origduration']
			self.AnalInterface.rawData[self.tgt.decompose['origfilename']] = {'info': {'channels': 1, 'lengthsec': self.tgt.decompose['origduration']}}

		#########################
		## CREATE OUTPUT FILES ##
		#########################
		self.p.logsection( "OUTPUT FILES" )
		allusedcpsfiles = list(set([oe.filename for oe in self.outputEvents]))
		
		
		#################
		## BACH output ##
		#################	
		if self.ops.BACH_FILEPATH != None:
			self.instruments.write(self.ops.get_outputfile('BACH_FILEPATH'), self.tgt.segs, self.cps.data['vcToCorpusName'], self.outputEvents, self.ops.BACH_SLOTS_MAPPING, self.ops.BACH_DB_TO_VELOCITY_BREAKPOINTS, self.ops.BACH_TARGET_STAFF, self.ops.BACH_CORPUS_STAFF, addTarget=self.ops.BACH_INCLUDE_TARGET)
			dict_of_files_written['BACH_FILEPATH'] = self.ops.get_outputfile('BACH_FILEPATH')


		################
		## AAF output ##
		################
		if self.ops.AAF_FILEPATH != None:
			import audioguide.fileoutput.aaf as aaf
			this_aaf = aaf.output(self.ops.get_outputfile('AAF_FILEPATH'))
			# add target ?
			if self.ops.AAF_INCLUDE_TARGET:
				this_aaf.addSoundfileResource(self.tgt.filename, self.AnalInterface.rawData[self.tgt.filename]['info'])
				sorted_tgt_tracks = concatenativeclasses.sortTargetSegmentsIntoTracks(self.tgt.segs, "minimum")
				this_aaf.add_tracks(sorted_tgt_tracks)
			# add selected corpus sounds
			for cpsfile in allusedcpsfiles:
				this_aaf.addSoundfileResource(cpsfile, self.AnalInterface.rawData[cpsfile]['info'])
			sorted_cps_tracks = concatenativeclasses.sortOutputEventsIntoTracks(self.outputEvents, self.ops.AAF_CPSTRACK_METHOD, self.cps.data['vcToCorpusName'], transpositionAffectsPlayspeed=False)
			this_aaf.add_tracks(sorted_cps_tracks)
			this_aaf.done(self.ops.AAF_AUTOLAUNCH)
			dict_of_files_written['AAF_FILEPATH'] = self.ops.get_outputfile('AAF_FILEPATH')
			self.p.log( "Wrote aaf file %s\n"%self.ops.get_outputfile('AAF_FILEPATH') )


		################
		## RPP output ##
		################
		if self.ops.RPP_FILEPATH != None:
			import audioguide.fileoutput.reaper as rpp
			import audioguide.takeenv_processor as takeenv_processor
			this_rpp = rpp.output(self.ops.get_outputfile('RPP_FILEPATH'))
			# add target?
			if self.ops.RPP_INCLUDE_TARGET:
				this_rpp.add_tracks(concatenativeclasses.sortTargetSegmentsIntoTracks(self.tgt.segs, "minimum"))
			# add selected corpus sounds
			corpus_tracks = concatenativeclasses.sortOutputEventsIntoTracks(self.outputEvents, self.ops.RPP_CPSTRACK_METHOD, self.cps.data['vcToCorpusName'], transpositionAffectsPlayspeed=self.ops.RPP_TRANS_AFFECTS_SPEED)
			# Process for TAKEENV if enabled
			if self.ops.ENABLE_TAKEENV:
				# Use PER_ITEM_GAIN if set (non-zero), otherwise fall back to STATIC_GAIN
				gain_db = self.ops.TAKEENV_PER_ITEM_GAIN if self.ops.TAKEENV_PER_ITEM_GAIN != 0.0 else self.ops.TAKEENV_STATIC_GAIN
				corpus_tracks = takeenv_processor.process_tracks_for_takeenv(
					corpus_tracks,
					enable_takeenv=True,
					static_gain_db=gain_db,
					dynamic=False
				)
			this_rpp.add_tracks(corpus_tracks)
			this_rpp.write(self.ops.RPP_AUTOLAUNCH, playrate_change_duration=self.ops.RPP_TRANS_AFFECTS_SPEED, enable_volumeenv=self.ops.ENABLE_SPECTRAL_VOLUMEENV)
			dict_of_files_written['RPP_FILEPATH'] = self.ops.get_outputfile('RPP_FILEPATH')
			self.p.log( "Wrote rpp file %s\n"%self.ops.get_outputfile('RPP_FILEPATH') )



		######################
		## dict output file ##
		######################
		if self.ops.DICT_OUTPUT_FILEPATH != None:
			output = {}
			output['opsfilename'] = self.ops.ops_file_path
			output['opsfiledata'] = self.ops.opsfileAsString
			# make target segment dict list
			self.tgt.segs.sort(key=operator.attrgetter('segmentStartSec'))
			tgtSegDataList = []
			for ts in self.tgt.segs:
				thisSeg = {'startSec': ts.segmentStartSec, 'endSec': ts.segmentEndSec}
				thisSeg['power'] = ts.desc.get('power-seg')
				thisSeg['numberSelectedUnits'] = ts.numberSelectedUnits
				thisSeg['has_been_mixed'] = ts.has_been_mixed
				tgtSegDataList.append(thisSeg)
			# finish up
			output['target'] = {'filename': self.tgt.filename, 'sfSkip': self.tgt.startSec, 'duration': self.tgt.endSec-self.tgt.startSec, 'segs': tgtSegDataList, 'fileduation': self.AnalInterface.rawData[self.tgt.filename]['info']['lengthsec'], 'chn': self.AnalInterface.rawData[self.tgt.filename]['info']['channels']} 
			output['corpus_file_list'] = list(set(allusedcpsfiles))
			output['selectedEvents'] = [oe.makeDictOutput() for oe in self.outputEvents]
			if eventsBool:
				output['outputparse'] = {'simultaneousSelections': int(max([d['simultaneousSelectionNumber'] for d in output['selectedEvents']])+1), 'classifications': max(self.ops.OUTPUTEVENT_CLASSIFY['numberClasses'], 1), 'corpusIds': int(max([d['corpusIdNumber'] for d in output['selectedEvents']])+1)}
			fh = open(self.ops.get_outputfile('DICT_OUTPUT_FILEPATH'), 'w')
			json.dump(output, fh)
			fh.close()
			dict_of_files_written['DICT_OUTPUT_FILEPATH'] = self.ops.get_outputfile('DICT_OUTPUT_FILEPATH')
			self.p.log( "Wrote JSON dict file %s\n"%self.ops.get_outputfile('DICT_OUTPUT_FILEPATH') )

		#####################################
		## maxmsp list output pour gilbert ##
		#####################################
		if self.ops.MAXMSP_OUTPUT_FILEPATH != None:
			output = {}
			output['target_file'] = [self.tgt.filename, self.tgt.startSec*1000., self.tgt.endSec*1000.]
			output['events'] = [oe.makeMaxMspListOutput() for oe in self.outputEvents]
			output['corpus_files'] = allusedcpsfiles
			fh = open(self.ops.get_outputfile('MAXMSP_OUTPUT_FILEPATH'), 'w')
			json.dump(output, fh)
			fh.close()
			dict_of_files_written['MAXMSP_OUTPUT_FILEPATH'] = self.ops.get_outputfile('MAXMSP_OUTPUT_FILEPATH')
			self.p.log( "Wrote MAX/MSP JSON lists to file %s\n"%self.ops.get_outputfile('MAXMSP_OUTPUT_FILEPATH') )

		###################################
		## superimpose label output file ##
		###################################
		if self.ops.OUTPUT_LABEL_FILEPATH != None:
			fh = open(self.ops.get_outputfile('OUTPUT_LABEL_FILEPATH'), 'w')
			fh.write( ''.join([ oe.makeLabelText() for oe in self.outputEvents ]) )
			fh.close()
			dict_of_files_written['OUTPUT_LABEL_FILEPATH'] = self.ops.get_outputfile('OUTPUT_LABEL_FILEPATH')
			self.p.log( "Wrote superimposition label file %s\n"%self.ops.get_outputfile('OUTPUT_LABEL_FILEPATH') )

		#######################################
		## corpus segmented features as json ##
		#######################################
		if self.ops.CORPUS_SEGMENTED_FEATURES_JSON_FILEPATH != None:
			fh = open(self.ops.get_outputfile('CORPUS_SEGMENTED_FEATURES_JSON_FILEPATH'), 'w')
			alldata = {}
			for c in self.cps.postLimitSegmentNormList:
				descs = {}
				for name, obj in c.desc.nameToObjMap.items():
					if name.find('-seg') != -1:
						descs[ name ] = obj.get(0, c.desc.len)
				alldata[(c.filename+'@'+str(c.segmentStartSec))] = descs
			json.dump(alldata, fh)
			fh.close()
			dict_of_files_written['CORPUS_SEGMENTED_FEATURES_JSON_FILEPATH'] = self.ops.get_outputfile('CORPUS_SEGMENTED_FEATURES_JSON_FILEPATH')
			self.p.log( "Wrote corpus segmented features file %s\n"%self.ops.get_outputfile('CORPUS_SEGMENTED_FEATURES_JSON_FILEPATH') )


		######################
		## lisp output file ##
		######################
		if self.ops.LISP_OUTPUT_FILEPATH != None:
			fh = open(self.ops.get_outputfile('LISP_OUTPUT_FILEPATH'), 'w')
			fh.write('(' + ''.join([ oe.makeLispText() for oe in self.outputEvents ]) +')')
			fh.close()
			dict_of_files_written['LISP_OUTPUT_FILEPATH'] = self.ops.get_outputfile('LISP_OUTPUT_FILEPATH')
			self.p.log( "Wrote lisp output file %s\n"%self.ops.get_outputfile('LISP_OUTPUT_FILEPATH') )

		########################################
		## data from segmentation file output ##
		########################################
		if self.ops.DATA_FROM_SEGMENTATION_FILEPATH != None:
			fh = open(self.ops.get_outputfile('DATA_FROM_SEGMENTATION_FILEPATH'), 'w')
			for line in [oe.makeSegmentationDataText() for oe in self.outputEvents]:
				fh.write(line)
			fh.close()
			dict_of_files_written['DATA_FROM_SEGMENTATION_FILEPATH'] = self.ops.get_outputfile('DATA_FROM_SEGMENTATION_FILEPATH')
			self.p.log( "Wrote data from segmentation file to textfile %s\n"%self.ops.get_outputfile('DATA_FROM_SEGMENTATION_FILEPATH') )

		############################
		## csound CSD output file ##
		############################
		if eventsBool and self.ops.CSOUND_CSD_FILEPATH != None and self.ops.CSOUND_RENDER_FILEPATH != None:
			from audioguide.fileoutput import csoundinterface as csd
			maxOverlaps = np.max([oe.simSelects for oe in self.outputEvents])
			csSco = 'i2  0.  %f  %f  "%s"  %f  %i\n\n'%(self.tgt.endSec-self.tgt.startSec, self.tgt.whole.envDb, self.tgt.filename, self.tgt.startSec, int(self.ops.CSOUND_CHANNEL_RENDER_METHOD == 'targetoutputmix'))
	
			# just in case that there are negative p2 times!
			minTime = min([ oe.timeInScore for oe in self.outputEvents ])
			if minTime < 0:
				for oe in self.outputEvents:
					oe.timeInScore -= minTime
			csSco += ''.join([ oe.makeCsoundOutputText(self.ops.CSOUND_CHANNEL_RENDER_METHOD) for oe in self.outputEvents ])
			csd.makeConcatenationCsdFile(self.ops.get_outputfile('CSOUND_CSD_FILEPATH', valid_extensions=['.csd']), self.ops.get_outputfile('CSOUND_RENDER_FILEPATH', valid_extensions=['.wav', '.aif', '.aiff']), self.ops.CSOUND_CHANNEL_RENDER_METHOD, self.ops.CSOUND_SR, self.ops.CSOUND_KSMPS, csSco, self.cps.len, set([oe.sfchnls for oe in self.outputEvents]), maxOverlaps, self.instruments, self.ops.OUTPUTEVENT_CLASSIFY['numberClasses'], bits=self.ops.CSOUND_BITS)
			dict_of_files_written['CSOUND_CSD_FILEPATH'] = self.ops.get_outputfile('CSOUND_CSD_FILEPATH')
			self.p.log( "Wrote csound csd file %s\n"%self.ops.get_outputfile('CSOUND_CSD_FILEPATH') )
			if self.ops.CSOUND_RENDER_FILEPATH != None:
				csd.render(self.ops.get_outputfile('CSOUND_CSD_FILEPATH', valid_extensions=['.csd']), len(self.outputEvents), printerobj=self.p)
				self.p.log( "Rendered csound soundfile output %s\n"%self.ops.get_outputfile('CSOUND_RENDER_FILEPATH') )
				dict_of_files_written['CSOUND_RENDER_FILEPATH'] = self.ops.get_outputfile('CSOUND_RENDER_FILEPATH')
	
			if self.ops.CSOUND_NORMALIZE:
				csd.normalize(self.ops.get_outputfile('CSOUND_RENDER_FILEPATH'), db=self.ops.CSOUND_NORMALIZE_PEAK_DB)
		################################
		## csound simple score output ##
		################################
		if eventsBool and self.ops.CSOUND_SCORE_FILEPATH != None:
			from audioguide.fileoutput import csoundinterface as csd
			csSco = csd.instru2helpstring()+'\n'
			csSco += ''.join([ oe.makeCsoundOutputText(self.ops.CSOUND_CHANNEL_RENDER_METHOD) for oe in self.outputEvents ])
			fh = open(self.ops.get_outputfile('CSOUND_SCORE_FILEPATH'), 'w')
			fh.write(csSco)
			fh.close()
		#######################
		## copy options file ##
		#######################
		if self.ops.COPY_OPTIONS_FILEPATH != None and self.ops.ops_file_path != None:
			import shutil
			shutil.copy(self.ops.ops_file_path, self.ops.get_outputfile('COPY_OPTIONS_FILEPATH'))
			dict_of_files_written['COPY_OPTIONS_FILEPATH'] = self.ops.get_outputfile('COPY_OPTIONS_FILEPATH')

		####################
		## close log file ##
		####################
		if self.ops.HTML_LOG_FILEPATH != None:
			self.p.writehtmllog(self.ops.get_outputfile('HTML_LOG_FILEPATH', valid_extensions=['.html']))
			dict_of_files_written['HTML_LOG_FILEPATH'] = self.ops.get_outputfile('HTML_LOG_FILEPATH')
		
		#######################################
		## check for lack of selected events ##
		#######################################
		if not eventsBool and self.ops.HTML_LOG_FILEPATH != None:
			util.error('CONCATENATION', "No segments were selected during concatenation. Check the log file %s for details."%self.ops.HTML_LOG_FILEPATH)
		elif not eventsBool:
			util.error('CONCATENATION', 'No segments were selected during concatenation. Try enabling the LOG file output to help figure out why. Use HTML_LOG_FILEPATH="valid/path"')
			
	
		if eventsBool and self.ops.CSOUND_CSD_FILEPATH != None and self.ops.CSOUND_RENDER_FILEPATH != None and self.ops.CSOUND_PLAY_RENDERED_FILE:
			csd.playFile( self.ops.get_outputfile('CSOUND_RENDER_FILEPATH') )

		return dict_of_files_written