############################################################################
## This software is distributed for free, without warranties of any kind. ##
## Send bug reports or suggestions to hackbarth@gmail.com                 ##
############################################################################
import os
import audioguide.util as util

'''Creates a rpp output file for reaper with TAKEENV clip gain automation support.'''

def db_to_linear(db):
	"""Convert dB to linear amplitude (for TAKEENV points)."""
	return 10 ** (db / 20.0)

def format_takeenv(gain_envelope, item_position):
	"""
	Format TAKEENV chunk with automation points.

	Args:
		gain_envelope: List of (time, gain_db) tuples - absolute timeline times
		item_position: Item start position in project timeline (used to convert to relative)

	Returns:
		Formatted TAKEENV string
	"""
	if not gain_envelope or len(gain_envelope) == 0:
		return ""

	# TAKEENV header (6 spaces - same level as SOURCE)
	takeenv_str = "      <TAKEENV\n"
	takeenv_str += "        NAME \"Volume\"\n"
	takeenv_str += "        ACT 1\n"  # Active
	takeenv_str += "        VIS 1\n"  # Visible
	takeenv_str += "        LANEHEIGHT 0 0\n"
	takeenv_str += "        ARM 0\n"  # Not armed
	takeenv_str += "        DEFSHAPE 0 -1 -1\n"  # Default shape

	# Add automation points
	# Convert absolute times to relative times (relative to item start)
	for time_sec, gain_db in gain_envelope:
		# Convert absolute time to relative time within the take
		relative_time = time_sec - item_position
		# Ensure non-negative (points can't be before item start)
		relative_time = max(0.0, relative_time)
		# Convert gain to linear (1.0 = 0dB)
		linear_value = db_to_linear(gain_db)
		# PT format: PT relative_time linear_value shape
		# Shape 0 = linear interpolation
		takeenv_str += "        PT %.6f %.6f 0\n" % (relative_time, linear_value)

	takeenv_str += "      >\n"
	return takeenv_str

def format_volumeenv(gain_envelope):
	"""
	Format VOLENV chunk for track-level volume automation.

	Args:
		gain_envelope: List of (time, gain_db) tuples

	Returns:
		Formatted VOLENV string for track-level automation
	"""
	if not gain_envelope or len(gain_envelope) == 0:
		return ""

	# VOLENV header (2 spaces - TRACK level)
	volenv_str = "  <VOLENV\n"
	volenv_str += "    ACT 1\n"  # Active
	volenv_str += "    VIS 1 1 1\n"  # Visible
	volenv_str += "    LANEHEIGHT 0 0\n"
	volenv_str += "    ARM 0\n"  # Not armed
	volenv_str += "    DEFSHAPE 0 -1 -1\n"  # Default shape (linear)

	# Add automation points
	for time_sec, gain_db in gain_envelope:
		# Convert gain_db to volume (Reaper track volume is in dB, but represented differently)
		# Reaper volume: 0.0 = -inf dB, 1.0 = 0 dB, 2.0 = +6dB
		# Formula: volume = 10^(dB/20)
		linear_value = db_to_linear(gain_db)
		# PT format: PT absolute_time value shape
		volenv_str += "    PT %.6f %.6f 0\n" % (time_sec, linear_value)

	volenv_str += "  >\n"
	return volenv_str

class output:
	def __init__(self, rpp_filepath):
		self.path = rpp_filepath
		self.tracks = []
	###########################################
	def add_tracks(self, tracks):
		self.tracks.extend(tracks)
	###########################################
	def write(self, autolaunchbool, verbose=True, rpp_header='REAPER_PROJECT 0.1 "6.11/x64" 1591355987', playrate_change_duration=True, playrate_preset=-1, enable_volumeenv=False, enable_takeenv=False):
		'''write and close the rpp file
		according to https://github.com/ReaTeam/Doc/blob/master/State%20Chunk%20Definitions

		Enhanced to support TAKEENV (clip gain automation) via 'gain_envelope' in item dict.
		'''
		f = open(self.path, "w")
		all_tracks_str = ''
		for trackname, trackitems, trackorigin in self.tracks:
			track_str = ''
			for d in trackitems:
				# Playback rate for transposition (if any)
				if playrate_change_duration:
					playrate_str = 'PLAYRATE %f 0 0 %i\n' % (1/d['transposeSpeedChange'], playrate_preset)
				else:
					playrate_str = 'PLAYRATE 1.000 1 %f %i\n' % (d['transposition'], playrate_preset)

				# Check if we have clip gain envelope automation
				has_envelope = 'gain_envelope' in d and d['gain_envelope'] and len(d['gain_envelope']) > 0
				
				# Generate TAKEENV string if envelope exists AND takeenv is enabled
				takeenv_str = ""
				if has_envelope and enable_takeenv:
					# time_sec relative to item start, but TAKEENV needs absolute position
					# Pass item position as offset so points are relative to item
					takeenv_str = format_takeenv(d['gain_envelope'], d['time'])

				# Calculate final volume (ampscale * static gain if present)
				final_volume = d['ampscale']
				if has_envelope and not enable_volumeenv and not enable_takeenv:
					# Extract static gain from first envelope point and multiply into VOLPAN
					# (only when VOLUMEENV is disabled and TAKEENV is not being written)
					_, gain_db = d['gain_envelope'][0]
					gain_linear = db_to_linear(gain_db)
					final_volume = d['ampscale'] * gain_linear

				# Use VOLPAN for clip gain (compatible with all Reaper versions)
				# Wrap SOURCE in TAKE if we have TAKEENV, otherwise use direct SOURCE
				if takeenv_str:
					# TAKEENV requires TAKE wrapper
					track_str += '''     <ITEM
      POSITION  %f
      NAME "%s"
      LENGTH %f
      SOFFS %f
      VOLPAN %f 0.0 1.0 -1.0
      FADEIN 1 %f 0.0
      FADEOUT 1 %f 0.0
      %s      <TAKE>
        <SOURCE WAVE>
          FILE "%s"
        >
%s      >
     >
''' % (d['time'], d['name'], d['orig_duration'], d['skip'], final_volume,
       d['fadein'], d['fadeout'], playrate_str, d['file'], takeenv_str)
				else:
					# Standard format without TAKE (no TAKEENV)
					track_str += '''     <ITEM
      POSITION  %f
      NAME "%s"
      LENGTH %f
      SOFFS %f
      VOLPAN %f 0.0 1.0 -1.0
      FADEIN 1 %f 0.0
      FADEOUT 1 %f 0.0
      %s      <SOURCE WAVE>
        FILE "%s"
      >
     >
''' % (d['time'], d['name'], d['orig_duration'], d['skip'], final_volume,
       d['fadein'], d['fadeout'], playrate_str, d['file'])

			# Check if we should add track-level VOLUMEENV automation
			volumeenv_str = ""
			if enable_volumeenv:
				# Extract gain_envelope from first item (for spectral reconstruction, one partial per track)
				if len(trackitems) > 0:
					first_item = trackitems[0]
					if 'gain_envelope' in first_item and first_item['gain_envelope'] and len(first_item['gain_envelope']) > 0:
						volumeenv_str = format_volumeenv(first_item['gain_envelope'])

			all_tracks_str += '''  <TRACK
   NAME "%s"
%s%s  >
''' % (trackname, track_str, volumeenv_str)

		f.write('''<%s
%s>''' % (rpp_header, all_tracks_str))
		f.close()

		# print
		tgt_track_count = len([t for t in self.tracks if t[0].find('target') != -1])
		if verbose and tgt_track_count == 0:
			print("Wrote %i corpus tracks to %s" % (len(self.tracks), self.path))
		elif verbose:
			print("Wrote %i target tracks and %i corpus tracks to %s" % (tgt_track_count, len(self.tracks)-tgt_track_count, self.path))

		# autolaunch?
		if autolaunchbool:
			import subprocess
			command = ['open', self.path]
			try:
				p = subprocess.Popen(command)
			except OSError:
				print('Auto launch command line call failed: \n\n"%s"' % ' '.join(command))
